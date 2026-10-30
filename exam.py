import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("exams", __name__, url_prefix="/exams", template_folder=".")
TITLE = "Exams"
TABLE = "EXAM"
ROLES = {'AR_OFFICER': 'SIUD'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Semester_ID": [r["Semester_ID"] for r in q("SELECT Semester_ID FROM SEMESTER ORDER BY 1")], "Course_Code": [r["Course_Code"] for r in q("SELECT Course_Code FROM COURSE ORDER BY 1")]}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Exam_ID`, `Semester_ID`, `Course_Code`, `Type`, `Date`, `Time` FROM EXAM")
    return render_template("exams_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Semester_ID', 'Course_Code', 'Type', 'Date', 'Time']
        try:
            q("INSERT INTO EXAM (`Semester_ID`, `Course_Code`, `Type`, `Date`, `Time`) VALUES (%s, %s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("exams.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("exams_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM EXAM WHERE `Exam_ID`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Semester_ID', 'Course_Code', 'Type', 'Date', 'Time']
        try:
            q("UPDATE EXAM SET `Semester_ID`=%s, `Course_Code`=%s, `Type`=%s, `Date`=%s, `Time`=%s WHERE `Exam_ID`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("exams.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("exams_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM EXAM WHERE `Exam_ID`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("exams.index"))


@bp.route("/exams.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "exams.css")
