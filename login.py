import os, time
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import check_password_hash
from common import q

bp = Blueprint("login", __name__, template_folder=".")
LOCK = {}   # username -> (failed attempts, locked until); 5 fails = 15 min lock


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"].strip()
        fails, until = LOCK.get(u, (0, 0))
        if until > time.time():
            flash("Account locked for 15 minutes.", "err")
        else:
            rows = q("SELECT * FROM USERS WHERE Username=%s", (u,))
            if rows and check_password_hash(rows[0]["Password_Hash"], request.form["password"]):
                LOCK.pop(u, None)
                session.update(role=rows[0]["Role"], name=rows[0]["First_Name"])
                return redirect(url_for("dashboard.index"))
            fails += 1
            LOCK[u] = (fails, time.time() + 900 if fails >= 5 else 0)
            flash("Invalid username or password.", "err")
    return render_template("login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login"))


@bp.route("/login.css")
def css():
    return send_from_directory(os.path.dirname(__file__), "login.css")
