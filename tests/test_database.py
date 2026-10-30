import unittest
from datetime import timedelta
from unittest.mock import patch

import mysql.connector
from flask import session

from app import create_app
from app.database.connection import close_connection, get_connection, query


class FakeCursor:
    def __init__(self, rows=None, failure=None):
        self.rows = rows or []
        self.failure = failure
        self.lastrowid = 0
        self.rowcount = 1
        self.closed = False

    def execute(self, _sql, _params):
        if self.failure:
            raise self.failure

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self.test_cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self, dictionary=False):
        if not dictionary:
            raise AssertionError("query helper must request dictionary rows")
        return self.test_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


class RoleCursor:
    def __init__(self):
        self.statements = []
        self.closed = False

    def execute(self, statement):
        self.statements.append(statement)

    def close(self):
        self.closed = True


class RoleConnection:
    def __init__(self):
        self.test_cursor = RoleCursor()
        self.closed = False

    def cursor(self):
        return self.test_cursor

    def close(self):
        self.closed = True


class DatabaseQueryTests(unittest.TestCase):
    def test_time_values_are_normalized_for_html_time_inputs(self):
        cursor = FakeCursor([{"Time": timedelta(hours=9)}])
        connection = FakeConnection(cursor)
        with patch("app.database.connection.get_connection", return_value=connection):
            rows = query("SELECT `Time` FROM LECTURE")
        self.assertEqual(rows[0]["Time"], "09:00:00")
        self.assertTrue(cursor.closed)

    def test_write_commits(self):
        cursor = FakeCursor()
        connection = FakeConnection(cursor)
        with patch("app.database.connection.get_connection", return_value=connection):
            result = query("INSERT INTO COURSE VALUES (%s)", ("ICT1407",), write=True)
        self.assertEqual(result, 1)
        self.assertEqual(connection.commits, 1)

    def test_failed_write_rolls_back_and_propagates_database_error(self):
        cursor = FakeCursor(failure=mysql.connector.Error("database failure"))
        connection = FakeConnection(cursor)
        with patch("app.database.connection.get_connection", return_value=connection):
            with self.assertRaises(mysql.connector.Error):
                query("INSERT INTO COURSE VALUES (%s)", ("ICT1407",), write=True)
        self.assertEqual(connection.rollbacks, 1)
        self.assertTrue(cursor.closed)

    def test_authenticated_connection_activates_only_the_assigned_role_before_use(self):
        app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        connection = RoleConnection()
        with app.test_request_context("/departments/"):
            session["role"] = "HOD"
            with patch(
                "app.database.connection.mysql.connector.connect",
                return_value=connection,
            ) as connect:
                self.assertIs(get_connection(), connection)
            self.assertNotIn("database", connect.call_args.kwargs)
            self.assertEqual(
                connection.test_cursor.statements,
                ["SET ROLE 'r_hod'@'%'", "USE `semester_mgt`"],
            )
            close_connection()
        self.assertTrue(connection.closed)

    def test_each_application_role_activates_exactly_its_mysql_role(self):
        app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        expected = {
            "AR_OFFICER": "r_ar",
            "HOD": "r_hod",
            "DEAN": "r_dean",
            "CLERK": "r_clerk",
        }
        for app_role, mysql_role in expected.items():
            connection = RoleConnection()
            with app.test_request_context("/"):
                session["role"] = app_role
                with patch(
                    "app.database.connection.mysql.connector.connect",
                    return_value=connection,
                ):
                    get_connection()
                self.assertEqual(
                    connection.test_cursor.statements,
                    [f"SET ROLE '{mysql_role}'@'%'", "USE `semester_mgt`"],
                )
                close_connection()

    def test_explicit_auth_query_replaces_a_cached_business_role_connection(self):
        app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        business_connection = RoleConnection()
        auth_connection = RoleConnection()
        with app.test_request_context("/login", method="POST"):
            session["role"] = "AR_OFFICER"
            with patch(
                "app.database.connection.mysql.connector.connect",
                side_effect=[business_connection, auth_connection],
            ):
                self.assertIs(get_connection(), business_connection)
                self.assertIs(get_connection(role="r_auth"), auth_connection)
            self.assertTrue(business_connection.closed)
            self.assertEqual(
                auth_connection.test_cursor.statements,
                ["SET ROLE 'r_auth'@'%'", "USE `semester_mgt`"],
            )
            close_connection()

    def test_unauthenticated_and_cli_connections_use_only_auth_role(self):
        app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        for context in (app.test_request_context("/login"), app.app_context()):
            connection = RoleConnection()
            with context:
                with patch(
                    "app.database.connection.mysql.connector.connect",
                    return_value=connection,
                ):
                    self.assertIs(get_connection(), connection)
                self.assertEqual(
                    connection.test_cursor.statements,
                    ["SET ROLE 'r_auth'@'%'", "USE `semester_mgt`"],
                )
                close_connection()

    def test_standalone_connection_uses_environment_and_auth_role(self):
        connection = RoleConnection()
        environment = {
            "DB_HOST": "db.example.test",
            "DB_USER": "semester_app",
            "DB_PASS": "not-logged",
            "DB_NAME": "semester_mgt",
            "DB_PORT": "3307",
            "DB_CONNECT_TIMEOUT": "7",
        }
        with patch.dict("os.environ", environment, clear=True):
            with patch(
                "app.database.connection.mysql.connector.connect",
                return_value=connection,
            ) as connect:
                self.assertIs(get_connection(), connection)
        self.assertEqual(connect.call_args.kwargs["host"], "db.example.test")
        self.assertNotIn("database", connect.call_args.kwargs)
        self.assertEqual(
            connection.test_cursor.statements,
            ["SET ROLE 'r_auth'@'%'", "USE `semester_mgt`"],
        )
        connection.close()


if __name__ == "__main__":
    unittest.main()
