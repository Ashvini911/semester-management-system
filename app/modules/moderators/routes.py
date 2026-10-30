import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("moderators", __name__, url_prefix="/moderators", template_folder=".")
TITLE = "Moderators"
TABLE = "MODERATOR"
ROLES = {'AR_OFFICER': 'SIUD'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Email`, `First_Name`, `Last_Name`, `Contact_No`, `Official_Address`, `Designation` FROM MODERATOR")
    return render_template("moderators_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Email', 'First_Name', 'Last_Name', 'Contact_No', 'Official_Address', 'Designation']
        try:
            q("INSERT INTO MODERATOR (`Email`, `First_Name`, `Last_Name`, `Contact_No`, `Official_Address`, `Designation`) VALUES (%s, %s, %s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("moderators.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("moderators_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM MODERATOR WHERE `Email`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['First_Name', 'Last_Name', 'Contact_No', 'Official_Address', 'Designation']
        try:
            q("UPDATE MODERATOR SET `First_Name`=%s, `Last_Name`=%s, `Contact_No`=%s, `Official_Address`=%s, `Designation`=%s WHERE `Email`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("moderators.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("moderators_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM MODERATOR WHERE `Email`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("moderators.index"))


@bp.route("/moderators.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "moderators.css")
