import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("semesters", __name__, url_prefix="/semesters", template_folder=".")
TITLE = "Semesters"
TABLE = "SEMESTER"
ROLES = {'AR_OFFICER': 'SIU', 'HOD': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Semester_ID`, `Academic_Year`, `Start_Date`, `End_Date` FROM SEMESTER")
    return render_template("semesters_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Semester_ID', 'Academic_Year', 'Start_Date', 'End_Date']
        try:
            q("INSERT INTO SEMESTER (`Semester_ID`, `Academic_Year`, `Start_Date`, `End_Date`) VALUES (%s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("semesters.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("semesters_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM SEMESTER WHERE `Semester_ID`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Academic_Year', 'Start_Date', 'End_Date']
        try:
            q("UPDATE SEMESTER SET `Academic_Year`=%s, `Start_Date`=%s, `End_Date`=%s WHERE `Semester_ID`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("semesters.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("semesters_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM SEMESTER WHERE `Semester_ID`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("semesters.index"))


@bp.route("/semesters.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "semesters.css")
