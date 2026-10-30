from threading import Lock
import time

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
import mysql.connector
from werkzeug.security import check_password_hash

from app.database.connection import query


bp = Blueprint("auth", __name__)
_attempts = {}
_attempts_lock = Lock()
_max_attempts = 5
_lock_seconds = 15 * 60


def _attempt_key(username):
    return (request.remote_addr or "unknown", username.casefold())


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        key = _attempt_key(username)
        now = time.monotonic()
        with _attempts_lock:
            stale_keys = [
                attempt_key
                for attempt_key, (_, _, expires_at) in _attempts.items()
                if expires_at <= now
            ]
            for attempt_key in stale_keys:
                _attempts.pop(attempt_key, None)
            attempt = _attempts.get(key)
            failures, locked_until = attempt[:2] if attempt else (0, 0)

        if locked_until:
            flash("Too many attempts. Try again in 15 minutes.", "error")
        else:
            try:
                users = query(
                    "SELECT Email, Username, First_Name, Role, Password_Hash "
                    "FROM USERS WHERE Username = %s",
                    (username,),
                    role="r_auth",
                )
            except mysql.connector.Error as error:
                if error.errno == 1044:
                    current_app.logger.error(
                        "MySQL denied database access during login lookup. "
                        "Verify the semester_app account host, r_auth assignment, "
                        "default role, and USERS SELECT grant."
                    )
                    flash(
                        "Database access is not configured for this application "
                        "account. Ask the administrator to verify semester_app "
                        "and r_auth in database/verify_permissions.sql.",
                        "error",
                    )
                elif error.errno == 1045:
                    current_app.logger.error(
                        "MySQL rejected the configured application credentials."
                    )
                    flash(
                        "Sign-in is temporarily unavailable. Check the database "
                        "account settings.",
                        "error",
                    )
                elif error.errno == 1142:
                    current_app.logger.error(
                        "MySQL denied the authentication query. Verify that "
                        "r_auth is active and has SELECT on semester_mgt.USERS."
                    )
                    flash(
                        "The authentication database role is missing permission "
                        "to look up users. Ask the administrator to verify r_auth.",
                        "error",
                    )
                elif error.errno == 3530:
                    current_app.logger.error(
                        "MySQL could not activate the authentication role. "
                        "Verify that r_auth exists and is granted to semester_app."
                    )
                    flash(
                        "The authentication database role is not assigned correctly. "
                        "Ask the administrator to verify r_auth.",
                        "error",
                    )
                else:
                    current_app.logger.exception("Login lookup failed")
                    flash(
                        "Sign-in is temporarily unavailable. Please try again later.",
                        "error",
                    )
            else:
                authenticated = False
                if users:
                    try:
                        authenticated = check_password_hash(
                            users[0]["Password_Hash"], password
                        )
                    except (TypeError, ValueError):
                        authenticated = False
                if authenticated and users[0]["Role"] in {
                    "AR_OFFICER", "HOD", "DEAN", "CLERK"
                }:
                    with _attempts_lock:
                        _attempts.pop(key, None)
                    user = users[0]
                    session.clear()
                    session.update(
                        email=user["Email"],
                        username=user["Username"],
                        name=user["First_Name"],
                        role=user["Role"],
                    )
                    session.permanent = True
                    return redirect(url_for("dashboard.index"))

                with _attempts_lock:
                    failures += 1
                    locked_until = now + _lock_seconds if failures >= _max_attempts else 0
                    _attempts[key] = (failures, locked_until, now + _lock_seconds)
                flash("Invalid username or password.", "error")
    return render_template("auth/login.html")


@bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
