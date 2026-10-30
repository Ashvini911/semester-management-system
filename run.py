import os, sys
from datetime import timedelta
from flask import Flask, flash, redirect, url_for
from werkzeug.security import generate_password_hash
from common import q
from pages import MODULES
from pages.login import login
from pages.dashboard import dashboard

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me")
app.permanent_session_lifetime = timedelta(minutes=15)   # 15 min inactivity timeout

app.register_blueprint(login.bp)
app.register_blueprint(dashboard.bp)
for m in MODULES:
    app.register_blueprint(m.bp)

app.context_processor(lambda: {"nav": [(m.bp.name + ".index", m.TITLE) for m in MODULES]})


@app.errorhandler(403)
def forbidden(_):
    flash("You do not have permission for that action.", "err")
    return redirect(url_for("dashboard.index"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "seed":   # python app.py seed
        q("UPDATE USERS SET Password_Hash=%s", (generate_password_hash("Demo@12345678"),), write=True)
        print("All sample users now have password: Demo@12345678")
    else:
        app.run(debug=True)
