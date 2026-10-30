import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("courses", __name__, url_prefix="/courses", template_folder=".")
TITLE = "Courses"
TABLE = "COURSE"
ROLES = {'AR_OFFICER': 'SIU', 'HOD': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Semester_ID": [r["Semester_ID"] for r in q("SELECT Semester_ID FROM SEMESTER ORDER BY 1")]}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Course_Code`, `Course_Name`, `Credit`, `Semester_ID` FROM COURSE")
    return render_template("courses_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Course_Code', 'Course_Name', 'Credit', 'Semester_ID']
        try:
            q("INSERT INTO COURSE (`Course_Code`, `Course_Name`, `Credit`, `Semester_ID`) VALUES (%s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("courses.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("courses_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM COURSE WHERE `Course_Code`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Course_Name', 'Credit', 'Semester_ID']
        try:
            q("UPDATE COURSE SET `Course_Name`=%s, `Credit`=%s, `Semester_ID`=%s WHERE `Course_Code`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("courses.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("courses_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM COURSE WHERE `Course_Code`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("courses.index"))


@bp.route("/courses.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "courses.css")
