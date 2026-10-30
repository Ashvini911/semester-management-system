import unittest
from unittest.mock import patch

from app import create_app


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        self.client = self.app.test_client()

    def _set_session(self, role):
        with self.client.session_transaction() as current_session:
            current_session["role"] = role
            current_session["name"] = "Test User"
            current_session["_csrf_token"] = "test-csrf-token"

    def test_all_blueprints_are_registered(self):
        expected = {
            "auth", "dashboard", "semesters", "courses", "timetables",
            "examinations", "lectures", "venues", "academic_staff",
            "departments", "degrees", "moderators",
        }
        self.assertTrue(expected.issubset(self.app.blueprints))

    def test_protected_page_redirects_to_login(self):
        response = self.client.get("/courses/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_development_bypass_redirects_login_and_uses_configured_role(self):
        app = create_app(
            {
                "TESTING": True,
                "DEBUG": True,
                "DEV_AUTH_BYPASS": True,
                "DEV_AUTH_ROLE": "HOD",
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        client = app.test_client()

        login_response = client.get("/login")
        self.assertEqual(login_response.status_code, 302)
        self.assertTrue(login_response.headers["Location"].endswith("/"))

        with patch("app.dashboard.routes.query", return_value=[{"total": 0}]):
            dashboard_response = client.get("/")
        self.assertEqual(dashboard_response.status_code, 200)
        with client.session_transaction() as current_session:
            self.assertEqual(current_session["role"], "HOD")
            self.assertEqual(current_session["username"], "developer")
        self.assertIn(b"Development bypass", dashboard_response.data)

        with patch("app.modules.crud.query", return_value=[]):
            department_response = client.get("/departments/")
        self.assertEqual(department_response.status_code, 200)

    def test_development_bypass_rejects_non_loopback_requests(self):
        app = create_app(
            {
                "TESTING": True,
                "DEBUG": True,
                "DEV_AUTH_BYPASS": True,
                "SECRET_KEY": "test-key-not-for-production",
            }
        )
        response = app.test_client().get(
            "/", environ_overrides={"REMOTE_ADDR": "192.0.2.1"}
        )
        self.assertEqual(response.status_code, 403)

    def test_development_bypass_requires_debug_mode_and_valid_role(self):
        base_config = {
            "TESTING": True,
            "DEV_AUTH_BYPASS": True,
            "SECRET_KEY": "test-key-not-for-production",
        }
        with self.assertRaisesRegex(RuntimeError, "requires debug mode"):
            create_app({**base_config, "DEBUG": False})
        with self.assertRaisesRegex(RuntimeError, "DEV_AUTH_ROLE"):
            create_app(
                {**base_config, "DEBUG": True, "DEV_AUTH_ROLE": "ADMIN"}
            )

    def test_every_management_list_template_renders_for_dean(self):
        self._set_session("DEAN")
        endpoints = (
            "/semesters/", "/courses/", "/timetables/", "/examinations/",
            "/lectures/", "/venues/", "/academic_staff/", "/departments/",
            "/degrees/", "/moderators/",
        )
        with patch("app.modules.crud.query", return_value=[]):
            for endpoint in endpoints:
                with self.subTest(endpoint=endpoint):
                    response = self.client.get(endpoint)
                    self.assertEqual(response.status_code, 200)

    def test_role_denied_from_manually_entered_url(self):
        self._set_session("HOD")
        response = self.client.get("/semesters/")
        self.assertEqual(response.status_code, 403)
        self.assertIn(b"Access denied", response.data)

    def test_missing_record_uses_custom_not_found_page(self):
        self._set_session("AR_OFFICER")
        with patch("app.modules.crud.query", return_value=[]):
            response = self.client.get("/courses/UNKNOWN/edit")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"could not be found", response.data)

    def test_clerk_cannot_delete_lecture_by_posting_directly(self):
        self._set_session("CLERK")
        response = self.client.post(
            "/lectures/1/delete",
            data={"_csrf_token": "test-csrf-token"},
        )
        self.assertEqual(response.status_code, 403)

    def test_clerk_lecture_form_populates_foreign_key_dropdowns(self):
        self._set_session("CLERK")
        options = [{"value": "V001", "label": "Example option"}]
        with patch("app.modules.crud.query", return_value=options):
            response = self.client.get("/lectures/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="Course_Code"', response.data)
        self.assertIn(b'name="Staff_ID"', response.data)
        self.assertRegex(
            response.get_data(as_text=True),
            r'<select[^>]*name="Venue_No"[^>]*required',
        )
        self.assertIn(b"Example option", response.data)

    def test_hod_department_edit_uses_a_database_backed_hod_dropdown(self):
        self._set_session("HOD")
        department = [{"Dep_Name": "Computing", "Email": "hod@example.com"}]
        hods = [{"value": "hod@example.com", "label": "hod@example.com"}]
        with patch(
            "app.modules.crud.query", side_effect=[department, hods]
        ):
            response = self.client.get("/departments/Computing/edit")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="Email"', response.data)
        self.assertIn(b'hod@example.com', response.data)

    def test_course_create_uses_lookup_and_parameterized_insert(self):
        self._set_session("AR_OFFICER")
        lookup = [{"value": "SEM1", "label": "SEM1"}]
        with patch("app.modules.crud.query", side_effect=[lookup, 1]) as database_query:
            response = self.client.post(
                "/courses/new",
                data={
                    "_csrf_token": "test-csrf-token",
                    "Course_Code": "ICT1407",
                    "Course_Name": "Database Systems",
                    "Credit": "1",
                    "Semester_ID": "SEM1",
                },
            )
        self.assertEqual(response.status_code, 302)
        insert_sql, insert_params = database_query.call_args_list[-1].args[:2]
        self.assertIn("INSERT INTO `COURSE`", insert_sql)
        self.assertEqual(insert_params, ("ICT1407", "Database Systems", 1, "SEM1"))

    def test_course_edit_updates_only_editable_fields(self):
        self._set_session("AR_OFFICER")
        existing = [{
            "Course_Code": "ICT1407",
            "Course_Name": "Database Systems",
            "Credit": 1,
            "Semester_ID": "SEM1",
        }]
        lookup = [{"value": "SEM1", "label": "SEM1"}]
        with patch(
            "app.modules.crud.query",
            side_effect=[existing, lookup, 1],
        ) as database_query:
            response = self.client.post(
                "/courses/ICT1407/edit",
                data={
                    "_csrf_token": "test-csrf-token",
                    "Course_Name": "Database Systems II",
                    "Credit": "3",
                    "Semester_ID": "SEM1",
                },
            )
        self.assertEqual(response.status_code, 302)
        update_sql, update_params = database_query.call_args_list[-1].args[:2]
        self.assertIn("UPDATE `COURSE`", update_sql)
        self.assertNotIn("`Course_Code` =", update_sql.split(" WHERE ", 1)[0])
        self.assertEqual(update_params, ("Database Systems II", 3, "SEM1", "ICT1407"))

    def test_course_delete_is_a_csrf_protected_post(self):
        self._set_session("AR_OFFICER")
        with patch("app.modules.crud.query", return_value=1) as database_query:
            response = self.client.post(
                "/courses/ICT1407/delete",
                data={"_csrf_token": "test-csrf-token"},
            )
        self.assertEqual(response.status_code, 302)
        self.assertIn("DELETE FROM `COURSE`", database_query.call_args.args[0])

    def test_invalid_course_credit_preserves_form_and_shows_error(self):
        self._set_session("AR_OFFICER")
        lookup = [{"value": "SEM1", "label": "SEM1"}]
        with patch("app.modules.crud.query", return_value=lookup):
            response = self.client.post(
                "/courses/new",
                data={
                    "_csrf_token": "test-csrf-token",
                    "Course_Code": "ICT1407",
                    "Course_Name": "Database Systems",
                    "Credit": "9",
                    "Semester_ID": "SEM1",
                },
            )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Credits must be no more than 6", response.data)
        self.assertIn(b'value="ICT1407"', response.data)

    def test_search_term_is_passed_as_a_bound_parameter(self):
        self._set_session("AR_OFFICER")
        search = "' OR 1=1 --"
        with patch("app.modules.crud.query", return_value=[]) as database_query:
            response = self.client.get("/courses/", query_string={"q": search})
        self.assertEqual(response.status_code, 200)
        sql, params = database_query.call_args.args
        self.assertNotIn(search, sql)
        self.assertEqual(params, tuple(f"%{search}%" for _ in range(3)))

    def test_static_css_and_javascript_are_served(self):
        css = self.client.get("/static/css/base.css")
        javascript = self.client.get("/static/js/main.js")
        self.assertEqual(css.status_code, 200)
        self.assertEqual(javascript.status_code, 200)
        css.close()
        javascript.close()

    def test_dashboard_uses_role_limited_database_counts(self):
        self._set_session("CLERK")
        with patch(
            "app.dashboard.routes.query",
            side_effect=[
                [{"total": 3}],
                [{"total": 5}],
                [{"total": 2}],
                [],
            ],
        ) as database_query:
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Upcoming examinations", response.data)
        self.assertEqual(database_query.call_count, 4)
        self.assertIn("EXAM", database_query.call_args_list[0].args[0])


if __name__ == "__main__":
    unittest.main()
