import os, datetime
from functools import wraps
import mysql.connector
from flask import session, redirect, url_for, abort

DBError = mysql.connector.Error


def q(sql, args=(), write=False):
    c = mysql.connector.connect(host=os.getenv("DB_HOST", "localhost"), user=os.getenv("DB_USER", "root"),
                                password=os.getenv("DB_PASS", ""), database=os.getenv("DB_NAME", "semester_mgt"))
    cur = c.cursor(dictionary=True)
    try:
        cur.execute(sql, args)
        if write:
            c.commit()
            return cur.lastrowid
        rows = cur.fetchall()
        for r in rows:                       # TIME columns -> "09:00:00" for <input type=time>
            for k, v in r.items():
                if isinstance(v, datetime.timedelta):
                    r[k] = str(v).rjust(8, "0")
        return rows
    finally:
        cur.close()
        c.close()


def perm(roles):
    return roles.get(session.get("role"), "") + "S"   # every logged-in role may view


def need(roles, action):
    if action not in perm(roles):
        abort(403)


def login_required(fn):
    @wraps(fn)
    def wrapper(*a, **k):
        if "role" not in session:
            return redirect(url_for("login.login"))
        session.permanent = True
        return fn(*a, **k)
    return wrapper
