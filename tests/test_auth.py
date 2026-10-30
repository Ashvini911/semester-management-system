import unittest
from unittest.mock import patch

import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from app.auth import routes as auth_routes


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        self.client = self.app.test_client()

    def _csrf_token(self):
        self.client.get("/login")
        with self.client.session_transaction() as current_session:
            return current_session["_csrf_token"]

    def test_password_hash_login_sets_session_and_redirects(self):
        user = {
            "Email": "ar@example.com",
            "Username": "amali_ar",
            "First_Name": "Amali",
            "Role": "AR_OFFICER",
            "Password_Hash": generate_password_hash("correct horse battery"),
        }
        with patch("app.auth.routes.query", return_value=[user]) as database_query:
            response = self.client.post(
                "/login",
                data={
                    "_csrf_token": self._csrf_token(),
                    "username": "amali_ar",
                    "password": "correct horse battery",
                },
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/")
        self.assertEqual(database_query.call_args.kwargs["role"], "r_auth")
        with self.client.session_transaction() as current_session:
            self.assertEqual(current_session["role"], "AR_OFFICER")
            self.assertEqual(current_session["email"], "ar@example.com")
            self.assertEqual(current_session["name"], "Amali")

    def test_invalid_password_does_not_authenticate(self):
        user = {
            "Email": "ar@example.com",
            "Username": "amali_ar",
            "First_Name": "Amali",
            "Role": "AR_OFFICER",
            "Password_Hash": generate_password_hash("correct horse battery"),
        }
        with patch("app.auth.routes.query", return_value=[user]):
            response = self.client.post(
                "/login",
                data={
                    "_csrf_token": self._csrf_token(),
                    "username": "amali_ar",
                    "password": "wrong password",
                },
            )
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as current_session:
            self.assertNotIn("role", current_session)
        self.assertIn(b"Invalid username or password", response.data)

    def test_repeated_login_failures_are_temporarily_limited(self):
        auth_routes._attempts.clear()
        user = {
            "Email": "ar@example.com",
            "Username": "amali_ar",
            "First_Name": "Amali",
            "Role": "AR_OFFICER",
            "Password_Hash": generate_password_hash("correct horse battery"),
        }
        with patch("app.auth.routes.query", return_value=[user]) as lookup:
            for _ in range(5):
                self.client.post(
                    "/login",
                    data={
                        "_csrf_token": self._csrf_token(),
                        "username": "amali_ar",
                        "password": "wrong password",
                    },
                )
            response = self.client.post(
                "/login",
                data={
                    "_csrf_token": self._csrf_token(),
                    "username": "amali_ar",
                    "password": "wrong password",
                },
            )
        self.assertEqual(lookup.call_count, 5)
        self.assertIn(b"Too many attempts", response.data)

    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post("/login", data={"username": "amali_ar"})
        self.assertEqual(response.status_code, 400)

    def test_database_privilege_error_shows_setup_guidance(self):
        with patch(
            "app.auth.routes.query",
            side_effect=mysql.connector.Error(
                msg="database access denied", errno=1044
            ),
        ):
            response = self.client.post(
                "/login",
                data={
                    "_csrf_token": self._csrf_token(),
                    "username": "amali_ar",
                    "password": "any password",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"database/verify_permissions.sql", response.data)
        self.assertNotIn(b"Traceback", response.data)

    def test_non_ascii_csrf_token_is_rejected_cleanly(self):
        token = self._csrf_token()
        response = self.client.post(
            "/login", data={"_csrf_token": f"{token}💥", "username": "amali_ar"}
        )
        self.assertEqual(response.status_code, 400)

    def test_logout_clears_session(self):
        with self.client.session_transaction() as current_session:
            current_session["role"] = "CLERK"
            current_session["email"] = "clerk@example.com"
            current_session["_csrf_token"] = "valid-token"
        response = self.client.post(
            "/logout", data={"_csrf_token": "valid-token"}
        )
        self.assertEqual(response.status_code, 302)
        with self.client.session_transaction() as current_session:
            self.assertEqual(dict(current_session), {})

    def test_password_reset_command_stores_only_a_hash(self):
        runner = self.app.test_cli_runner()
        with patch(
            "app.database.connection.query",
            side_effect=[[{"Email": "ar@example.com"}], 1],
        ) as database_query:
            result = runner.invoke(
                args=["set-password", "ar@example.com"],
                input="new secure password\nnew secure password\n",
            )
        self.assertEqual(result.exit_code, 0, result.output)
        password_hash = database_query.call_args.args[1][0]
        self.assertNotEqual(password_hash, "new secure password")
        self.assertTrue(
            check_password_hash(password_hash, "new secure password")
        )


if __name__ == "__main__":
    unittest.main()
