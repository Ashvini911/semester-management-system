import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("departments", __name__, url_prefix="/departments", template_folder=".")
TITLE = "Departments"
TABLE = "DEPARTMENT"
ROLES = {'HOD': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Email": [r["Email"] for r in q("SELECT Email FROM HOD ORDER BY 1")]}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Dep_Name`, `Email` FROM DEPARTMENT")
    return render_template("departments_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Dep_Name', 'Email']
        try:
            q("INSERT INTO DEPARTMENT (`Dep_Name`, `Email`) VALUES (%s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("departments.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("departments_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM DEPARTMENT WHERE `Dep_Name`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Email']
        try:
            q("UPDATE DEPARTMENT SET `Email`=%s WHERE `Dep_Name`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("departments.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("departments_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM DEPARTMENT WHERE `Dep_Name`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("departments.index"))


@bp.route("/departments.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "departments.css")
