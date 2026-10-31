from ipaddress import ip_address
import secrets
from datetime import timedelta
from hmac import compare_digest

from flask import Flask, abort, redirect, render_template, request, session, url_for
import click
import mysql.connector
from werkzeug.security import generate_password_hash

from app.config import Config
from app.database.connection import close_connection
from app.modules import BLUEPRINTS
from app.services.permission_service import navigation_for


def create_app(test_config=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("Set SECRET_KEY in the environment before starting the application.")
    if app.config["DEV_AUTH_BYPASS"]:
        valid_roles = {"AR_OFFICER", "HOD", "DEAN", "CLERK"}
        role = app.config["DEV_AUTH_ROLE"]
        if not app.debug:
            raise RuntimeError("Development authentication bypass requires debug mode.")
        if role not in valid_roles:
            raise RuntimeError("DEV_AUTH_ROLE must be AR_OFFICER, HOD, DEAN, or CLERK.")

    app.permanent_session_lifetime = timedelta(
        minutes=app.config["SESSION_LIFETIME_MINUTES"]
    )
    app.teardown_appcontext(close_connection)

    from app.auth.routes import bp as auth_bp
    from app.dashboard.routes import bp as dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)

    @app.before_request
    def protect_forms():
        if app.config["DEV_AUTH_BYPASS"]:
            remote_addr = request.remote_addr
            try:
                is_loopback = bool(remote_addr and ip_address(remote_addr).is_loopback)
            except ValueError:
                is_loopback = False
            if not app.debug or not is_loopback:
                abort(403)

            role = app.config["DEV_AUTH_ROLE"]
            if session.get("role") != role or session.get("username") != "developer":
                session.clear()
                session.update(
                    email="developer@localhost",
                    username="developer",
                    name="Development User",
                    role=role,
                )
            if request.endpoint == "auth.login":
                return redirect(url_for("dashboard.index"))

        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        expected = session.get("_csrf_token")
        supplied = request.form.get("_csrf_token") or request.headers.get(
            "X-CSRF-Token", ""
        )
        if (
            not isinstance(expected, str)
            or not isinstance(supplied, str)
            or not compare_digest(
                expected.encode("utf-8"), supplied.encode("utf-8")
            )
        ):
            abort(400)
        return None

    @app.context_processor
    def template_context():
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_urlsafe(32)
        return {
            "csrf_token": session["_csrf_token"],
            "navigation": navigation_for(session.get("role")),
            "dev_auth_bypass": app.config["DEV_AUTH_BYPASS"],
        }

    @app.cli.command("set-password")
    @click.argument("email")
    def set_password(email):
        password = click.prompt(
            "New password (minimum 12 characters)",
            hide_input=True,
            confirmation_prompt=True,
        )
        if len(password) < 12:
            raise click.ClickException("Password must contain at least 12 characters.")
        from app.database.connection import query

        if not query(
            "SELECT Email FROM USERS WHERE Email = %s",
            (email,),
            role="r_auth",
        ):
            raise click.ClickException("No user exists with that email address.")
        query(
            "UPDATE USERS SET Password_Hash = %s WHERE Email = %s",
            (generate_password_hash(password), email),
            write=True,
            role="r_auth",
        )
        click.echo("Password updated.")

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(mysql.connector.Error)
    def database_unavailable(error):
        app.logger.error("Database error: %s", error)
        return render_template("errors/503.html"), 503

    @app.errorhandler(500)
    def internal_error(_error):
        return render_template("errors/500.html"), 500

    return app
