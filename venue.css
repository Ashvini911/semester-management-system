import os
from flask import send_from_directory, Blueprint, render_template, request, redirect, url_for, flash, abort
from common import q, login_required, need, perm, DBError

bp = Blueprint("venues", __name__, url_prefix="/venues", template_folder=".")
TITLE = "Venues"
TABLE = "VENUE"
ROLES = {'AR_OFFICER': 'SIU', 'CLERK': 'SIU'}   # S=view I=add U=edit D=delete (from the report's privilege table)


def lookups():
    """Dropdown options for the form."""
    return {"Venue_Type": ['LAB', 'LECTURE_HALL']}


@bp.route("/")
@login_required
def index():
    rows = q("SELECT `Venue_No`, `Venue_Name`, `Capacity`, `Floor`, `Building`, `Venue_Type` FROM VENUE")
    return render_template("venues_list.html", rows=rows, perm=perm(ROLES), title=TITLE)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    need(ROLES, "I")
    if request.method == "POST":
        cols = ['Venue_No', 'Venue_Name', 'Capacity', 'Floor', 'Building', 'Venue_Type']
        try:
            q("INSERT INTO VENUE (`Venue_No`, `Venue_Name`, `Capacity`, `Floor`, `Building`, `Venue_Type`) VALUES (%s, %s, %s, %s, %s, %s)",
              [request.form.get(c) or None for c in cols], write=True)
            flash("Saved.", "ok")
            return redirect(url_for("venues.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
    return render_template("venues_form.html", row=request.form, lookups=lookups(), editing=False, title=TITLE)


@bp.route("/<key>/edit", methods=["GET", "POST"])
@login_required
def edit(key):
    need(ROLES, "U")
    found = q("SELECT * FROM VENUE WHERE `Venue_No`=%s", (key,))
    if not found:
        abort(404)
    row = found[0]
    if request.method == "POST":
        cols = ['Venue_Name', 'Capacity', 'Floor', 'Building', 'Venue_Type']
        try:
            q("UPDATE VENUE SET `Venue_Name`=%s, `Capacity`=%s, `Floor`=%s, `Building`=%s, `Venue_Type`=%s WHERE `Venue_No`=%s",
              [request.form.get(c) or None for c in cols] + [key], write=True)
            flash("Updated.", "ok")
            return redirect(url_for("venues.index"))
        except DBError as ex:
            flash("Database error: " + ex.msg, "err")
            row = request.form
    return render_template("venues_form.html", row=row, lookups=lookups(), editing=True, title=TITLE)


@bp.route("/<key>/delete", methods=["POST"])
@login_required
def delete(key):
    need(ROLES, "D")
    try:
        q("DELETE FROM VENUE WHERE `Venue_No`=%s", (key,), write=True)
        flash("Deleted.", "ok")
    except DBError as ex:
        flash("Cannot delete: " + ex.msg, "err")
    return redirect(url_for("venues.index"))


@bp.route("/venues.css")
def css():
    """Serves this page's own stylesheet (only the .css file, never the source)."""
    return send_from_directory(os.path.dirname(__file__), "venues.css")
