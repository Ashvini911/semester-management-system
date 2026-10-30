import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("degrees", __name__, url_prefix="/degrees", template_folder=".")
TITLE = "Degrees"
TABLE = "DEGREE"
ROLES = {'HOD': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Dep_Name": [r["Dep_Name"] for r in q("SELECT Dep_Name FROM DEPARTMENT ORDER BY 1")]}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Degree_Name`, `Credit`, `Duration`, `Dep_Name` FROM DEGREE")
    return render_template("degrees_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Degree_Name', 'Credit', 'Duration', 'Dep_Name']
        try:
            q("INSERT INTO DEGREE (`Degree_Name`, `Credit`, `Duration`, `Dep_Name`) VALUES (%s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("degrees.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("degrees_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM DEGREE WHERE `Degree_Name`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Credit', 'Duration', 'Dep_Name']
        try:
            q("UPDATE DEGREE SET `Credit`=%s, `Duration`=%s, `Dep_Name`=%s WHERE `Degree_Name`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("degrees.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("degrees_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM DEGREE WHERE `Degree_Name`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("degrees.index"))


@bp.route("/degrees.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "degrees.css")
