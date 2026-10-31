#!/usr/bin/env python
"""Verify database connectivity and the application's role-based read access."""

import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import mysql.connector


ROLE_TABLES = {
    "r_auth": ("USERS",),
    "r_ar": (
        "SEMESTER",
        "COURSE",
        "EXAM",
        "TIME_TABLE",
        "LECTURE",
        "ACADEMIC_STAFF_MEMBER",
        "VENUE",
        "MODERATOR",
    ),
    "r_hod": ("DEPARTMENT", "DEGREE", "HOD"),
    "r_dean": (
        "DEPARTMENT",
        "DEGREE",
        "SEMESTER",
        "TIME_TABLE",
        "COURSE",
        "ACADEMIC_STAFF_MEMBER",
        "VENUE",
        "MODERATOR",
        "SECOND_EXAMINER",
        "LECTURE",
        "EXAM",
        "DEMONSTRATOR",
        "REQUIREMENT",
        "DEMONSTRATOR_REQUIREMENT",
    ),
    "r_clerk": (
        "LECTURE",
        "EXAM",
        "VENUE",
        "COURSE",
        "SEMESTER",
        "ACADEMIC_STAFF_MEMBER",
        "MODERATOR",
    ),
}

REQUIRED_ENV = ("SECRET_KEY", "DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME")
PLACEHOLDERS = {
    "SECRET_KEY": "replace-with-a-secure-random-key",
    "DB_PASS": "replace-with-your-database-password",
}


def report(label, result):
    print(f"{label:<28}: {result}")


def check_configuration():
    missing = [
        key
        for key in REQUIRED_ENV
        if not os.getenv(key) or not os.getenv(key).strip()
    ]
    placeholders = [
        key for key, value in PLACEHOLDERS.items() if os.getenv(key) == value
    ]
    try:
        port = int(os.getenv("DB_PORT", ""))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        missing.append("DB_PORT (must be an integer from 1 to 65535)")
    if missing:
        return False, "Missing or invalid: " + ", ".join(missing)
    if placeholders:
        return False, "Replace template values for: " + ", ".join(placeholders)
    return True, "OK"


def check_permissions(cursor, database):
    missing_tables = []
    denied_access = []
    missing_roles = []
    safe_database = database.replace("`", "``")

    for role, tables in ROLE_TABLES.items():
        try:
            cursor.execute(f"SET ROLE '{role}'@'%'")
        except mysql.connector.Error as error:
            missing_roles.append(f"{role} (MySQL {error.errno})")
            continue

        for table in tables:
            try:
                cursor.execute(
                    f"SELECT 1 FROM `{safe_database}`.`{table}` LIMIT 0"
                )
            except mysql.connector.Error as error:
                if error.errno == 1146:
                    missing_tables.append(table)
                else:
                    denied_access.append(f"{role}:{table} (MySQL {error.errno})")

    if missing_roles or missing_tables or denied_access:
        details = []
        if missing_roles:
            details.append("roles unavailable: " + ", ".join(missing_roles))
        if missing_tables:
            details.append("tables missing: " + ", ".join(sorted(set(missing_tables))))
        if denied_access:
            details.append("SELECT denied: " + ", ".join(denied_access))
        return False, "; ".join(details)
    return True, "OK (role activation and SELECT access checked)"


def main():
    print("====================================")
    print(" SEMESTER MANAGEMENT SYSTEM")
    print(" DATABASE VERIFICATION")
    print("====================================")

    python_ok = sys.version_info >= (3, 10)
    python_status = (
        f"OK ({sys.version_info.major}.{sys.version_info.minor})"
        if python_ok
        else "FAIL (Python 3.10+ required)"
    )
    report("Python environment", python_status)
    if not python_ok:
        return 1

    load_dotenv(Path(__file__).resolve().with_name(".env"))
    config_ok, config_message = check_configuration()
    report("Environment configuration", config_message)
    if not config_ok:
        report("MySQL server", "NOT CHECKED")
        report("Database connection", "NOT CHECKED")
        report("Database", "NOT CHECKED")
        report("Required tables", "NOT CHECKED")
        report("Application permissions", "NOT CHECKED")
        return 1

    try:
        port = int(os.environ["DB_PORT"])
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            port=port,
            connection_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        )
    except (mysql.connector.Error, ValueError) as error:
        code = getattr(error, "errno", None)
        if code in (1045, 1130):
            server_status = "OK (reachable; account authentication was rejected)"
            connection_status = (
                "FAIL (check DB_USER, DB_PASS, and the MySQL account host)"
            )
        elif code in (2002, 2003, 2005):
            server_status = (
                "FAIL (unreachable; check DB_HOST, DB_PORT, and MySQL service)"
            )
            connection_status = "FAIL"
        else:
            server_status = (
                f"FAIL (connection error{f' {code}' if code else ''}; "
                "check MySQL settings)"
            )
            connection_status = "FAIL"
        report("MySQL server", server_status)
        report("Database connection", connection_status)
        report("Database", "NOT CHECKED")
        report("Required tables", "NOT CHECKED")
        report("Application permissions", "NOT CHECKED")
        return 1

    report("MySQL server", "OK")
    database = os.environ["DB_NAME"]
    cursor = connection.cursor(buffered=True)
    try:
        try:
            cursor.execute("SET ROLE 'r_auth'@'%'")
        except mysql.connector.Error as error:
            report(
                "Database connection",
                f"FAIL (r_auth role unavailable; MySQL {error.errno})",
            )
            report("Database", "NOT CHECKED")
            report("Required tables", "NOT CHECKED")
            report("Application permissions", "FAIL")
            return 1

        safe_database = database.replace("`", "``")
        try:
            cursor.execute(f"USE `{safe_database}`")
        except mysql.connector.Error as error:
            if error.errno == 1049:
                message = f"FAIL (database {database!r} does not exist)"
            elif error.errno == 1044:
                message = f"FAIL (semester_app cannot use {database!r}; check role grants)"
            else:
                message = f"FAIL (MySQL {error.errno}; check database configuration)"
            report("Database connection", "FAIL")
            report(f"Database: {database}", message)
            report("Required tables", "NOT CHECKED")
            report("Application permissions", "NOT CHECKED")
            return 1

        report("Database connection", "OK")
        report(f"Database: {database}", "OK")
        permissions_ok, permission_message = check_permissions(cursor, database)
        if permissions_ok:
            report("Required tables", "OK")
            report("Application permissions", permission_message)
            print("\nDatabase verification completed.")
            print("Note: write and denied-operation grants are covered by Database/check_connection.py.")
            return 0

        report("Required tables", "FAIL (see permission details)")
        report("Application permissions", "FAIL (" + permission_message + ")")
        print(
            "\nDatabase verification failed. Follow database/README.md "
            "to configure the schema and roles."
        )
        return 1
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
