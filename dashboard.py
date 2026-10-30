import os
from flask import Blueprint, render_template, send_from_directory
from common import q, login_required

bp = Blueprint("dashboard", __name__, template_folder=".")


@bp.route("/")
@login_required
def index():
    from pages import MODULES
    cards = [(m.bp.name + ".index", m.TITLE, q("SELECT COUNT(*) AS n FROM " + m.TABLE)[0]["n"]) for m in MODULES]
    upcoming = q("SELECT Course_Code, `Type`, `Date`, `Time` FROM EXAM WHERE `Date` >= CURDATE() ORDER BY `Date` LIMIT 5")
    return render_template("dashboard.html", cards=cards, upcoming=upcoming)


@bp.route("/dashboard.css")
def css():
    return send_from_directory(os.path.dirname(__file__), "dashboard.css")
