# Database files

- `schema.sql` is the canonical, non-destructive schema for a new empty
  `semester_mgt` database. It preserves the tables, constraints and views in
  the supplied project schema.
- `sample_data.sql` inserts the assignment's sample academic records. The
  sample account hashes are deliberately unusable until reset with the Flask
  `set-password` command.
- `roles.sql` creates and grants the MySQL roles used by the application. It
  assumes the runtime account `semester_app`@`localhost` already exists and
  limits the Dean role to explicit academic tables, not authentication records.
- `verify_permissions.sql` contains read-only MySQL Workbench checks for account,
  role, grant, default-role and effective privilege configuration.
- `check_connection.py` checks a live connection with the application's `.env`
  settings, tests role activation and expected allowed/denied access, and can
  optionally verify a user's Werkzeug password hash.
- `full_database_dump.sql` is the supplied MySQL dump, including sample data
  and `DROP TABLE` statements. Restore it only into a disposable database.
- `legacy_setup.sql` is the supplied setup/query script retained for reference.
  It includes stale `S1-2026` examples and role grants without the corresponding
  role creation statements; prefer the canonical files above for new setups.

The app's `r_auth` role can read user identities and update only password
hashes. Each business role follows the privilege matrix documented in the
project README. Additional `SELECT` grants on related tables are limited to
the foreign-key dropdowns and joined list pages needed by AR officers, HODs
and clerks. No schema migration is required for these grants.

The schema and sample data scripts are intended for a fresh database. They
use `CREATE` and `INSERT` statements and are not an upgrade script for a
populated production database.

## MySQL Workbench setup

For a **fresh** database, run these steps in order from a Workbench SQL tab
connected as a MySQL administrator:

1. Open `schema.sql` and execute it against the server.
2. Open `sample_data.sql` and execute it only if the sample records are wanted.
3. Create the runtime account with a strong, unique password. Replace the
   placeholder locally; do not save a real password into a project script:

   ```sql
   CREATE USER 'semester_app'@'localhost'
     IDENTIFIED BY 'replace-this-with-a-strong-secret';
   ```

4. Open `roles.sql` and execute it. It creates the role definitions, grants
   them to `semester_app`, and makes `r_auth` the account's default role.
5. Open `verify_permissions.sql` and execute it as the administrator to inspect
   the account, role assignments, default role and effective grants.

For an **already imported database**, do not run `schema.sql`,
`sample_data.sql`, or `full_database_dump.sql`. In Workbench, connect as the
administrator for the same MySQL server used by Flask and run these checks:

```sql
SELECT User, Host, is_role
FROM mysql.user
WHERE (User = 'semester_app' AND Host = 'localhost')
   OR User IN ('r_auth', 'r_ar', 'r_hod', 'r_dean', 'r_clerk');

SELECT @@hostname, @@port;
```

If `semester_app` does not exist, create it using step 3 above. Then open and execute only `roles.sql`; it does not drop tables or modify
academic data. It replaces the Dean role's broad database-level read grant
with explicit academic-table grants, so `r_dean` cannot read password hashes
or other authentication records. Reapply it to an existing setup to enforce
that narrower privilege.
Afterward execute `verify_permissions.sql`. If the runtime account has old
direct grants, inspect `SHOW GRANTS FOR 'semester_app'@'localhost'` and remove
only privileges that the administrator has confirmed are unnecessary. This
file intentionally does not revoke unknown existing grants.

The Flask connector deliberately connects without choosing a database first.
It then activates exactly `r_auth` for login/CLI password resets, or exactly
the logged-in user's business role, and only then executes `USE semester_mgt`.
This avoids requesting database access before the role grants are active.
Environment variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASS`
must match the server and account shown in Workbench. Do not configure the
Flask application to use `root`.

To test the live setup after `.env` is configured, run from the project root:

```sh
.venv/bin/python database/check_connection.py
```

This performs read-only `SELECT`s and zero-row `INSERT`/`UPDATE`/`DELETE`
permission probes; the probes do not create or alter any records. It expects
unauthorized operations to be rejected. Optionally enter a username and its
password when prompted to verify the stored Werkzeug hash. The password input
is hidden and is not logged. Password changes remain an explicit separate
operation using `flask --app run.py set-password <email>`.
