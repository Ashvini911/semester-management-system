import os
import unittest
from unittest.mock import patch

import mysql.connector

from check_database import ROLE_TABLES, check_configuration, check_permissions


VALID_CONFIGURATION = {
    "SECRET_KEY": "test-secret",
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_USER": "semester_app",
    "DB_PASS": "test-password",
    "DB_NAME": "semester_mgt",
}


class CheckDatabaseTests(unittest.TestCase):
    def test_configuration_rejects_template_password(self):
        configuration = {
            **VALID_CONFIGURATION,
            "DB_PASS": "replace-with-your-database-password",
        }
        with patch.dict(os.environ, configuration, clear=True):
            valid, message = check_configuration()

        self.assertFalse(valid)
        self.assertIn("DB_PASS", message)

    def test_configuration_accepts_complete_values(self):
        with patch.dict(os.environ, VALID_CONFIGURATION, clear=True):
            valid, message = check_configuration()

        self.assertTrue(valid)
        self.assertEqual(message, "OK")

    def test_role_permissions_check_expected_read_tables(self):
        class Cursor:
            def __init__(self):
                self.statements = []

            def execute(self, statement):
                self.statements.append(statement)

        cursor = Cursor()
        valid, message = check_permissions(cursor, "semester_mgt")

        self.assertTrue(valid)
        self.assertIn("SELECT access checked", message)
        self.assertEqual(
            sum(statement.startswith("SELECT 1 FROM") for statement in cursor.statements),
            sum(len(tables) for tables in ROLE_TABLES.values()),
        )
        self.assertEqual(
            sum(statement.startswith("SET ROLE") for statement in cursor.statements),
            len(ROLE_TABLES),
        )

    def test_missing_table_is_reported(self):
        class Cursor:
            def execute(self, statement):
                if statement == "SELECT 1 FROM `semester_mgt`.`SEMESTER` LIMIT 0":
                    raise mysql.connector.Error(
                        msg="table missing",
                        errno=1146,
                    )

        valid, message = check_permissions(Cursor(), "semester_mgt")

        self.assertFalse(valid)
        self.assertIn("tables missing: SEMESTER", message)


if __name__ == "__main__":
    unittest.main()
