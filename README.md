# Semester Management System

A Flask and MySQL application for managing academic semesters and related
records for the ICT 1407 Database Systems assignment. It keeps the original
MySQL schema and provides session authentication, role-based access, dashboards
and data-management screens.

## Features

- Password-hash-based sign-in, sign-out, session expiration and CSRF protection.
- Server-enforced role authorization with matching MySQL roles.
- Role-filtered navigation and dashboard totals from MySQL.
- Searchable, reusable CRUD pages with validation and related-record dropdowns.
- Responsive interface, accessible navigation, flash feedback and error pages.

## Technologies

- Python 3.10 or later
- Flask, Jinja2 and Werkzeug
- MySQL 8.0 and `mysql-connector-python`
- HTML, CSS and a small vanilla JavaScript file

## Project layout

```text
app/
  auth/                 Authentication routes
  dashboard/            Role-aware dashboard
  database/             Connection and query helpers
  modules/              Academic CRUD Blueprints and reusable CRUD renderer
  services/              Authorization policy
  static/css/            Shared responsive styles
  static/js/             Small navigation/confirmation interactions
  templates/             Shared, auth, dashboard and error templates
database/                Canonical schema, sample data, roles and supplied SQL
tests/                    Unit tests using a mocked database
run.py                    Application entry point
```

## Prerequisites

- Python 3.10+
- MySQL Server 8.0
- A MySQL account with permission to create the database and roles during setup

## MySQL setup

For a fresh database, follow the exact Workbench execution order and commands
in [`database/README.md`](database/README.md). For an existing imported
database, run **only** `database/roles.sql` as a MySQL administrator; do not
re-run the schema or sample data scripts. Then run the read-only
[`database/verify_permissions.sql`](database/verify_permissions.sql).

If Flask reports MySQL error 1044, check the exact server/host/database in
`.env`, then run
[`database/check_connection.py`](database/check_connection.py) with the
configured `semester_app` account. It connects without selecting a database,
activates the expected role, selects `semester_mgt`, verifies permitted reads,
and confirms unauthorized operations are rejected. The verification script
identifies where role activation or database selection fails. Never run the
Flask application using MySQL's root account.

`database/full_database_dump.sql` is the supplied dump and contains destructive
`DROP TABLE` statements. Use it only to restore a disposable database, never as
an upgrade against existing data. The original mixed-purpose script remains as
`database/legacy_setup.sql` for reference.

The sample users have usernames `amali_ar`, `kamal_hod`, `nimal_dean` and
`saman_clerk`. Their password hashes are placeholders. After configuring the
application, run `flask --app run.py set-password <email>` once for each sample
account to set passwords interactively.

## Python setup and run

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a fresh `SECRET_KEY` and the database connection values in `.env`, then run:

```sh
python run.py
```

The app listens on `http://127.0.0.1:5000`. `SESSION_COOKIE_SECURE` should be
`true` when deployed behind HTTPS. Do not use Flask's development server for
production.

For local UI development only, set `DEV_AUTH_BYPASS=true` in `.env` to open
the dashboard without signing in. The default demo role is `AR_OFFICER`;
set `DEV_AUTH_ROLE` to `AR_OFFICER`, `HOD`, `DEAN`, or `CLERK` to choose another
role, then restart with `python run.py`. This mode is debug-only and restricted
to loopback requests (`127.0.0.1`/`::1`); the app still uses MySQL and enforces
the selected role's database and application permissions. Keep the setting
false for normal use and never enable it in a deployed environment.

## Roles and permissions

| Role | Application access | MySQL role |
|---|---|---|
| AR_OFFICER | Create, view, update and delete semesters, courses, timetables, examinations and lectures | `r_ar` |
| HOD | View and update departments and degrees | `r_hod` |
| DEAN | Read academic information across the system | `r_dean` |
| CLERK | View venues; create and view lectures and examinations | `r_clerk` |

The application activates exactly one MySQL role per connection: `r_auth`
during login and CLI password resets, or the user's business role for
authenticated requests. Database permissions are a second boundary; routes
still check their permissions before reading or writing. Related-table
`SELECT` grants support only the foreign-key dropdowns and joined records
needed for the allowed workflows (including the HOD lookup); they do not add
those modules to role navigation.
The Dean's MySQL grants are limited to academic tables and exclude `USERS`
and other authentication records.

The login attempt limiter is process-local and protects against repeated
attempts within one running worker. It resets on restart and is not shared
between multiple workers. Use a shared rate-limit/lockout store for a
multi-worker production deployment.

## Tests

The unit tests do not require a live MySQL server:

```sh
python -m unittest discover -s tests -v
```

They verify application/Blueprint setup, authentication behavior, CSRF checks,
role authorization and representative CRUD paths with database queries mocked.
Run a separate integration test against a disposable MySQL database to verify
real permissions, schema setup and database writes.

## Database source notes

The project originally included a schema/setup script and a separate MySQL
dump. The dump contains table data and destructive drop statements; the setup
script mixes schema, sample data, reporting queries and partial role grants.
The new canonical files separate those purposes without changing the existing
table design. See [`database/README.md`](database/README.md) for details.
