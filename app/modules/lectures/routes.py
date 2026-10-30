import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("lectures", __name__, url_prefix="/lectures", template_folder=".")
TITLE = "Lectures"
TABLE = "LECTURE"
ROLES = {'AR_OFFICER': 'SIUD', 'HOD': 'SU', 'CLERK': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Course_Code": [r["Course_Code"] for r in q("SELECT Course_Code FROM COURSE ORDER BY 1")], "Staff_ID": [r["Staff_ID"] for r in q("SELECT Staff_ID FROM ACADEMIC_STAFF_MEMBER ORDER BY 1")], "Venue_No": [r["Venue_No"] for r in q("SELECT Venue_No FROM VENUE ORDER BY 1")], "Moderator_Email": [r["Email"] for r in q("SELECT Email FROM MODERATOR ORDER BY 1")], "Mode": ['Physical', 'Online']}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Lecture_ID`, `Course_Code`, `Staff_ID`, `Venue_No`, `Moderator_Email`, `Date`, `Time`, `Mode` FROM LECTURE")
    return render_template("lectures_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Course_Code', 'Staff_ID', 'Venue_No', 'Moderator_Email', 'Date', 'Time', 'Mode']
        try:
            q("INSERT INTO LECTURE (`Course_Code`, `Staff_ID`, `Venue_No`, `Moderator_Email`, `Date`, `Time`, `Mode`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("lectures.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("lectures_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM LECTURE WHERE `Lecture_ID`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Course_Code', 'Staff_ID', 'Venue_No', 'Moderator_Email', 'Date', 'Time', 'Mode']
        try:
            q("UPDATE LECTURE SET `Course_Code`=%s, `Staff_ID`=%s, `Venue_No`=%s, `Moderator_Email`=%s, `Date`=%s, `Time`=%s, `Mode`=%s WHERE `Lecture_ID`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("lectures.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("lectures_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM LECTURE WHERE `Lecture_ID`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("lectures.index"))


@bp.route("/lectures.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "lectures.css")
