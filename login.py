from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Demo login account
USERNAME = "student"
PASSWORD_HASH = generate_password_hash("12345")


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
        return "<h1>Login Successful!</h1><p>Welcome Student!</p>"

    else:
        return render_template(
            "login.html",
            message="Invalid username or password!"
        )


if __name__ == "__main__":
    app.run(debug=True)