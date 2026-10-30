import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("staff", __name__, url_prefix="/staff", template_folder=".")
TITLE = "Academic Staff"
TABLE = "ACADEMIC_STAFF_MEMBER"
ROLES = {'HOD': 'SIU', 'CLERK': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Staff_Type": ['LECTURER', 'VISITING', 'INTERNAL'], "Employment": ['PERMANENT', 'TEMPORARY']}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Staff_ID`, `First_Name`, `Last_Name`, `Email`, `Contact_No`, `Staff_Type`, `Employment` FROM ACADEMIC_STAFF_MEMBER")
    return render_template("staff_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Staff_ID', 'First_Name', 'Last_Name', 'Email', 'Contact_No', 'Staff_Type', 'Employment']
        try:
            q("INSERT INTO ACADEMIC_STAFF_MEMBER (`Staff_ID`, `First_Name`, `Last_Name`, `Email`, `Contact_No`, `Staff_Type`, `Employment`) VALUES (%s, %s, %s, %s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("staff.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("staff_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM ACADEMIC_STAFF_MEMBER WHERE `Staff_ID`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['First_Name', 'Last_Name', 'Email', 'Contact_No', 'Staff_Type', 'Employment']
        try:
            q("UPDATE ACADEMIC_STAFF_MEMBER SET `First_Name`=%s, `Last_Name`=%s, `Email`=%s, `Contact_No`=%s, `Staff_Type`=%s, `Employment`=%s WHERE `Staff_ID`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("staff.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("staff_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM ACADEMIC_STAFF_MEMBER WHERE `Staff_ID`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("staff.index"))


@bp.route("/staff.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "staff.css")
