#!/usr/bin/env python3
"""Verify the live MySQL account's role activation and effective permissions."""

from getpass import getpass
import os
import sys

from dotenv import load_dotenv
import mysql.connector
from werkzeug.security import check_password_hash


ROLE_TABLES = {
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
USER_ROLE_NAMES = {
    "AR_OFFICER": "r_ar",
    "HOD": "r_hod",
    "DEAN": "r_dean",
    "CLERK": "r_clerk",
}


def activate(cursor, role):
    cursor.execute(f"SET ROLE '{role}'@'%'")


def verify_allowed_tables(cursor, tables):
    for table in tables:
        cursor.execute(f"SELECT 1 FROM `{table}` LIMIT 0")
    return len(tables)


def verify_denied(cursor, statement, label):
    try:
        cursor.execute(statement)
    except mysql.connector.Error as error:
        if error.errno not in {1044, 1142, 1143}:
            raise
        print(f"PASS: denied as expected: {label} (MySQL {error.errno})")
    else:
        raise RuntimeError(
            f"FAIL: {label} succeeded; semester_app has excess privileges."
        )


def verify_noop_insert(cursor, table, columns, select_values):
    columns_sql = ", ".join(f"`{column}`" for column in columns)
    values_sql = ", ".join(select_values)
    cursor.execute(
        f"INSERT INTO `{table}` ({columns_sql}) "
        f"SELECT {values_sql} WHERE 1 = 0"
    )


def main():
    load_dotenv()
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "semester_app"),
            password=os.getenv("DB_PASS", ""),
            port=int(os.getenv("DB_PORT", "3306")),
            connection_timeout=int(os.getenv("DB_CONNECT_TIMEOUT", "5")),
        )
        cursor = connection.cursor(buffered=True)
        try:
            activate(cursor, "r_auth")
            database = os.getenv("DB_NAME", "semester_mgt").replace("`", "``")
            cursor.execute(f"USE `{database}`")
            cursor.execute(
                "SELECT @@hostname, @@port, DATABASE(), CURRENT_USER(), CURRENT_ROLE()"
            )
            server, port, db_name, account, active_role = cursor.fetchone()
            print(
                f"Connected: server={server}:{port}, database={db_name}, "
                f"account={account}, role={active_role}; configured "
                f"host={os.getenv('DB_HOST', 'localhost')}:"
                f"{os.getenv('DB_PORT', '3306')}, "
                f"database={os.getenv('DB_NAME', 'semester_mgt')}"
            )

            cursor.execute(
                "SELECT Email, Username, First_Name, Last_Name, Role, Password_Hash "
                "FROM USERS ORDER BY Username LIMIT 1"
            )
            sample_user = cursor.fetchone()
            if sample_user is None:
                raise RuntimeError("r_auth can read USERS, but the table has no user rows.")
            print(
                "PASS: r_auth can query USERS "
                f"(sample username={sample_user[1]}, role={sample_user[4]})."
            )

            cursor.execute(
                "UPDATE USERS SET Password_Hash = Password_Hash WHERE 1 = 0"
            )
            connection.rollback()
            print("PASS: r_auth has the password-hash update privilege.")
            verify_denied(
                cursor,
                "SELECT Course_Code FROM COURSE LIMIT 0",
                "r_auth reading academic tables",
            )

            username = input(
                "Username to verify a stored Werkzeug password hash (blank to skip): "
            ).strip()
            if username:
                cursor.execute(
                    "SELECT Password_Hash, Role FROM USERS WHERE Username = %s",
                    (username,),
                )
                account_row = cursor.fetchone()
                if account_row is None:
                    raise RuntimeError("No account matches that username.")
                password = getpass("Password to verify (input is hidden): ")
                if not check_password_hash(account_row[0], password):
                    raise RuntimeError("The password does not match the stored hash.")
                user_role = account_row[1]
                print(f"PASS: Werkzeug password hash verified for role {user_role}.")
            else:
                user_role = None

            for role, tables in ROLE_TABLES.items():
                activate(cursor, role)
                count = verify_allowed_tables(cursor, tables)
                print(f"PASS: {role} can SELECT from {count} required table(s).")
                if role == "r_ar":
                    verify_noop_insert(
                        cursor,
                        "SEMESTER",
                        ("Semester_ID", "Academic_Year", "Start_Date", "End_Date"),
                        ("'VERIFY'", "'VERIFY'", "CURRENT_DATE()", "CURRENT_DATE()"),
                    )
                    cursor.execute(
                        "UPDATE SEMESTER SET Academic_Year = Academic_Year WHERE 1 = 0"
                    )
                    cursor.execute("DELETE FROM SEMESTER WHERE 1 = 0")
                    verify_denied(
                        cursor,
                        "UPDATE DEPARTMENT SET Dep_Name = Dep_Name WHERE 1 = 0",
                        "r_ar updating departments",
                    )
                elif role == "r_hod":
                    cursor.execute(
                        "UPDATE DEPARTMENT SET Dep_Name = Dep_Name WHERE 1 = 0"
                    )
                    cursor.execute("UPDATE DEGREE SET Credit = Credit WHERE 1 = 0")
                    verify_denied(
                        cursor,
                        "SELECT Course_Code FROM COURSE LIMIT 0",
                        "r_hod reading courses",
                    )
                elif role == "r_dean":
                    verify_denied(
                        cursor,
                        "SELECT Password_Hash FROM USERS LIMIT 0",
                        "r_dean reading authentication records",
                    )
                elif role == "r_clerk":
                    verify_noop_insert(
                        cursor,
                        "EXAM",
                        ("Semester_ID", "Course_Code", "Type", "Date", "Time"),
                        ("'VERIFY'", "'VERIFY'", "'VERIFY'", "CURRENT_DATE()", "CURRENT_TIME()"),
                    )
                    verify_noop_insert(
                        cursor,
                        "LECTURE",
                        ("Course_Code", "Staff_ID", "Venue_No", "Date", "Time", "Mode"),
                        ("'VERIFY'", "'VERIFY'", "'VERIFY'", "CURRENT_DATE()", "CURRENT_TIME()", "'Online'"),
                    )
                    verify_denied(
                        cursor,
                        "UPDATE VENUE SET Venue_Name = Venue_Name WHERE 1 = 0",
                        "r_clerk updating venues",
                    )
                connection.rollback()

            if user_role:
                role = USER_ROLE_NAMES[user_role]
                activate(cursor, role)
                cursor.execute("SELECT 1")
                print(f"PASS: authenticated role {role} activates.")
            print("Permission verification completed.")
        finally:
            cursor.close()
    except (mysql.connector.Error, RuntimeError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    finally:
        if connection is not None:
            connection.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
