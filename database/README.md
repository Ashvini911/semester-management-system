# MySQL database setup

The application uses a dedicated `semester_app` MySQL account with narrowly
scoped roles. Do not run Flask as MySQL `root`, and do not grant unrestricted
database privileges to the application account.

## Install and start MySQL

1. Install **MySQL Server 8.0** and **MySQL Workbench** on the computer. During
   installation, record the administrator password privately.
2. Start the MySQL service. On Windows, confirm that the configured MySQL
   service (often `MySQL80`) is running in Windows Services or MySQL Installer.
   On macOS, start the service using the MySQL preference pane or the service
   manager used by that installation.
3. Open MySQL Workbench and connect to the local server as a MySQL
   administrator. Confirm the connection's host and port (normally
   `localhost:3306`).

## Create a new database

For a **fresh, empty** database, use Workbench as an administrator and run
these files in order:

1. Open and execute `database/schema.sql`. It creates `semester_mgt` and its tables.
2. Open and execute `database/sample_data.sql` if the sample academic records and users
   are wanted. Sample user password hashes are placeholders.
3. Create a dedicated runtime account, using a strong unique password locally:

   ```sql
   CREATE USER 'semester_app'@'localhost'
     IDENTIFIED BY 'replace-this-with-a-strong-secret';
   ```

   Do not save the real password in a project SQL file or commit it.
4. Open and execute `database/roles.sql`. It creates the application roles, grants them
   to `semester_app`, and makes `r_auth` the account's default role.
5. Open and execute `database/verify_permissions.sql` as the administrator to inspect
   the account, role assignments, default role and grants.

`roles.sql` assumes `semester_app`@`localhost` already exists. If the Flask
configuration connects from a different host, create the matching MySQL user
host entry and update the grants deliberately rather than broadening privileges.

## Existing database

For a database that has already been imported, do not rerun
`database/schema.sql` or `database/sample_data.sql`. Do not run
`database/full_database_dump.sql`. Confirm which MySQL
server and database contain the data. If needed, create the runtime account
using step 3 above, then apply only `roles.sql` and run
`database/verify_permissions.sql`. `database/roles.sql` is designed to add/enforce the roles
without dropping tables or changing academic data.

`database/full_database_dump.sql` contains destructive `DROP TABLE` statements. Use it
only to restore a **disposable** database whose existing data may be destroyed.
`database/legacy_setup.sql`, `database/semestermgt file.sql` and
`database/sm sql.sql` are retained source
files and are not the canonical setup path.

## Configure the application

From the project root, copy `.env.example` to `.env` if setup has not already
created it. Set the local database values to match Workbench and the account:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=semester_app
DB_PASS=your-local-semester_app-password
DB_NAME=semester_mgt
```

Keep the generated `SECRET_KEY` private. `.env` is local and ignored by Git;
never paste credentials into `.env.example`, SQL scripts, screenshots, or logs.
The application deliberately connects without selecting a database first,
activates `r_auth` or a business role, and then selects `semester_mgt`. This is
necessary for MySQL role-based grants to take effect.

## Verify connection and permissions

Run the connection and schema/read-access check from the project root.

Windows:

```powershell
.\.venv\Scripts\python.exe check_database.py
```

macOS:

```sh
.venv/bin/python check_database.py
```

It reports unreachable MySQL, rejected credentials, a missing database, missing
tables, unavailable roles, and denied `SELECT` access separately. It never
prints `DB_PASS` and makes no database changes. It checks required role
activation and read access only.

For deeper application-account checks, run the existing
`database/check_connection.py`. It verifies role activation, allowed reads,
representative write grants and expected denied operations using zero-row
probes; it can optionally check a stored Werkzeug password hash. The probes do
not insert or modify records. `database/verify_permissions.sql` provides administrator
side grant and role checks.

If MySQL reports error 1044 or access denied, confirm the configured host,
database and account, and then inspect the grant and default-role results from
`verify_permissions.sql`. Do not fix permission errors by granting
`ALL PRIVILEGES` to `semester_app`.

## Set sample account passwords

After `.env` and MySQL are configured, run the CLI from the project root to
set passwords interactively. The password is hidden and stored as a Werkzeug
hash. Setup does not reset existing passwords:

```powershell
.\.venv\Scripts\flask.exe --app run.py set-password ar@example.com
.\.venv\Scripts\flask.exe --app run.py set-password hod@example.com
.\.venv\Scripts\flask.exe --app run.py set-password dean@example.com
.\.venv\Scripts\flask.exe --app run.py set-password clerk@example.com
```
