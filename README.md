# Semester Management System

A Flask application for managing academic semesters and related records for
the ICT 1407 Database Systems assignment. It provides authenticated,
role-based dashboards and data-management pages backed by MySQL.

## Project overview

- Password-hash-based sign-in, sign-out, session expiration and CSRF protection.
- Server-enforced role authorization backed by MySQL roles.
- Searchable CRUD pages for the academic modules.
- Responsive HTML templates, CSS and a small vanilla JavaScript file.

## Technologies

- **Python 3.10+** runs the application and its setup utilities.
- **Flask** handles routing, sessions, the CLI and the local development server.
- **Jinja2** renders the HTML templates.
- **MySQL 8.0** stores the application records and enforces database roles.
- **mysql-connector-python** connects Flask to MySQL.
- **HTML, CSS and JavaScript** provide the browser interface.

## Project structure

```text
app/
  auth/                 Authentication routes
  dashboard/            Role-aware dashboard
  database/             Connection and query helpers
  modules/              Academic CRUD Blueprints and reusable CRUD renderer
  services/              Authorization policy
  static/                CSS, images and JavaScript
  templates/             Shared, auth, dashboard and error templates
database/
  schema.sql             Canonical schema for an empty database
  sample_data.sql        Sample academic records and accounts
  roles.sql              Least-privilege MySQL roles
  verify_permissions.sql Read-only MySQL role and grant checks
  check_connection.py    Live role and operation permission checks
tests/                    Unit tests using a mocked database
check_database.py         Connection, schema and read-permission verification
setup_windows.ps1         Windows Python environment setup
start_windows.ps1         Windows application launcher
run.py                    Application entry point and Flask CLI
```

## Requirements

- Python 3.10 or later (64-bit recommended).
- MySQL Server 8.0 and MySQL Workbench.
- A MySQL administrator account for first-time database and role setup.
- A separate `semester_app` account for the application; do not use `root` in
  the Flask configuration.

## Windows installation

Open PowerShell and run:

```powershell
git clone YOUR_REPOSITORY_URL
cd semester-management-system
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_windows.ps1
```

The execution-policy command is only needed if PowerShell blocks the scripts.
It applies to the current PowerShell process only. Setup uses the Windows
Python launcher (`py`) when available, creates `.venv`, installs the packages
from `requirements.txt`, verifies their imports, and creates `.env` from
`.env.example` only when `.env` does not already exist. It generates a local
random `SECRET_KEY`; it never replaces an existing `.env`.

If Python 3.10+ is not installed, install it first from
[python.org](https://www.python.org/downloads/windows/) or the Microsoft Store,
then reopen PowerShell and rerun setup. If setup reports that an existing
`.venv` is not a Windows environment, rename that environment yourself and
rerun the script; setup will not remove or overwrite it.

## Environment configuration

Edit `.env` in the project root and set `DB_HOST`, `DB_PORT`, `DB_USER`,
`DB_PASS`, and `DB_NAME` to match the local MySQL server and runtime account.
Do not share or commit `.env`; `.gitignore` excludes it. `.env.example` contains
only placeholders. Never put a real password or secret key in that template.

`DEV_AUTH_BYPASS` is disabled by default. It is only for local UI development,
requires debug mode, and is restricted to loopback requests. Keep it disabled
for normal use and never enable it in a deployed environment.

## MySQL database setup

Follow [database/README.md](database/README.md) for installing and starting
MySQL, creating or importing `semester_mgt`, applying the sample data and
least-privilege roles, and testing the connection. For a fresh database, use
`database/schema.sql`, optionally `database/sample_data.sql`, then create the
`semester_app` account and run `database/roles.sql`.

Do **not** execute `database/full_database_dump.sql` during normal setup. It
contains destructive `DROP TABLE` statements and is only for restoring a
disposable database. Do not rerun schema or sample-data scripts against an
existing database.

Once `.env` and the database are configured, verify connection, expected
tables, and role-based read access with:

```powershell
.\.venv\Scripts\python.exe check_database.py
```

This verification does not print the database password and does not make
database changes. It checks read access and role activation; run
`database/check_connection.py` for deeper checks of expected write and denied
operations.

## Set initial sample passwords

The sample account hashes are placeholders. After configuring the database,
set each account's password through the Flask CLI. It prompts for the new
password without echoing it and stores a Werkzeug password hash. No password
is reset automatically:

```powershell
.\.venv\Scripts\flask.exe --app run.py set-password ar@example.com
.\.venv\Scripts\flask.exe --app run.py set-password hod@example.com
.\.venv\Scripts\flask.exe --app run.py set-password dean@example.com
.\.venv\Scripts\flask.exe --app run.py set-password clerk@example.com
```

## Run the application

On Windows, from the project root:

```powershell
.\start_windows.ps1
```

On macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Set a private `SECRET_KEY` and the correct database values in `.env`, then run:

```sh
python run.py
```

The server listens at [http://127.0.0.1:5000](http://127.0.0.1:5000). For
macOS, use `python -m flask --app run.py set-password <email>` to set account
passwords. The app uses Flask's development server; do not use it in production.
Set `SESSION_COOKIE_SECURE=true` when deployed behind HTTPS.

## Roles and permissions

| Role | Application access | MySQL role |
|---|---|---|
| AR_OFFICER | Create, view, update and delete semesters, courses, timetables, examinations and lectures | `r_ar` |
| HOD | View and update departments and degrees | `r_hod` |
| DEAN | Read academic information across the system | `r_dean` |
| CLERK | View venues; create and view lectures and examinations | `r_clerk` |

The application activates exactly one MySQL role per connection: `r_auth`
during login and CLI password resets, or the user's business role for
authenticated requests. Routes also enforce their application permissions.
The Dean's database grants exclude `USERS` and other authentication records.

## Troubleshooting

- **`ModuleNotFoundError` or `No module named 'dotenv'`:** run
  `.\setup_windows.ps1` again. Start the app with `.\start_windows.ps1` so it
  uses `.venv`, not a different system Python. On macOS, activate `.venv` and
  run `python -m pip install -r requirements.txt`.
- **python-dotenv is missing after setup:** run
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`; ensure
  `python-dotenv` (with the hyphen) is in `requirements.txt`.
- **`mysql.connector` import or connection error:** install packages with
  setup, then check `DB_HOST`, `DB_PORT`, `DB_USER` and `DB_PASS` in `.env`.
- **MySQL service is not running:** start the MySQL80 (or configured MySQL)
  service from Windows Services / MySQL Installer, or start the MySQL service
  using the service manager on macOS.
- **Access denied for `semester_app`:** verify the account host matches the
  connection host and that `database/roles.sql` was applied by a MySQL
  administrator. Do not substitute `root` in the app configuration.
- **Unknown database `semester_mgt`:** create/import the schema using the
  safe instructions in [database/README.md](database/README.md); never restore
  the destructive dump into a database with data to preserve.
- **`.env` is missing:** rerun setup (Windows) or copy `.env.example` to `.env`
  (macOS), then set a private key and database credentials.
- **Incorrect database password:** update `DB_PASS` in your local `.env` to
  the `semester_app` password; do not share or commit the file.
- **PowerShell execution policy blocks scripts:** run
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in the current
  PowerShell window, then retry.
- **Port 5000 is already in use:** stop the other local development server,
  or identify its process and choose an available port by changing the
  `app.run` port in `run.py` for local development.

## Tests

The unit tests use mocked database access and do not require a live MySQL
server. Run them with the project environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

For macOS, use `python -m unittest discover -s tests -v` after activating
`.venv`. Database role, schema, and write-permission checks require a configured
live MySQL server.
