from functools import wraps

from flask import abort, redirect, session, url_for

from app.services.permission_service import has_permission


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("role"):
            return redirect(url_for("auth.login"))
        session.permanent = True
        return view(*args, **kwargs)

    return wrapped


def permission_required(module, action):
    def decorate(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not has_permission(session.get("role"), module, action):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorate
