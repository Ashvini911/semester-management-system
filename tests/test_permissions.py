import unittest

from app.services.permission_service import MODULE_ACCESS, has_permission, navigation_for


class PermissionTests(unittest.TestCase):
    def test_ar_officer_can_manage_academic_planning(self):
        for module in ("semesters", "courses", "timetables", "examinations", "lectures"):
            for action in ("R", "C", "U", "D"):
                with self.subTest(module=module, action=action):
                    self.assertTrue(has_permission("AR_OFFICER", module, action))

    def test_hod_can_only_read_and_update_department_records(self):
        for module in ("departments", "degrees"):
            self.assertTrue(has_permission("HOD", module, "R"))
            self.assertTrue(has_permission("HOD", module, "U"))
            self.assertFalse(has_permission("HOD", module, "C"))
            self.assertFalse(has_permission("HOD", module, "D"))
        self.assertFalse(has_permission("HOD", "semesters", "R"))

    def test_clerk_can_read_venues_and_create_exams_and_lectures(self):
        self.assertTrue(has_permission("CLERK", "venues", "R"))
        for module in ("lectures", "examinations"):
            self.assertTrue(has_permission("CLERK", module, "R"))
            self.assertTrue(has_permission("CLERK", module, "C"))
            self.assertFalse(has_permission("CLERK", module, "U"))
            self.assertFalse(has_permission("CLERK", module, "D"))

    def test_dean_has_read_only_access_to_all_registered_modules(self):
        for module in MODULE_ACCESS:
            self.assertTrue(has_permission("DEAN", module.slug, "R"))
            self.assertFalse(has_permission("DEAN", module.slug, "C"))

    def test_navigation_contains_only_readable_modules(self):
        nav = navigation_for("CLERK")
        slugs = {item["endpoint"].split(".", 1)[0] for item in nav}
        self.assertEqual(slugs, {"venues", "lectures", "examinations"})
        self.assertEqual(navigation_for(None), [])


if __name__ == "__main__":
    unittest.main()
