from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleAccess:
    slug: str
    title: str
    endpoint: str
    group: str
    table: str
    actions: dict


MODULE_ACCESS = (
    ModuleAccess(
        "semesters", "Semesters", "semesters.index", "Academic planning",
        "SEMESTER", {"AR_OFFICER": frozenset("CRUD"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "courses", "Courses", "courses.index", "Academic planning",
        "COURSE", {"AR_OFFICER": frozenset("CRUD"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "timetables", "Timetables", "timetables.index", "Academic planning",
        "TIME_TABLE", {"AR_OFFICER": frozenset("CRUD"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "examinations", "Examinations", "examinations.index", "Academic planning",
        "EXAM", {
            "AR_OFFICER": frozenset("CRUD"),
            "CLERK": frozenset("RC"),
            "DEAN": frozenset("R"),
        },
    ),
    ModuleAccess(
        "lectures", "Lectures", "lectures.index", "Academic planning",
        "LECTURE", {
            "AR_OFFICER": frozenset("CRUD"),
            "CLERK": frozenset("RC"),
            "DEAN": frozenset("R"),
        },
    ),
    ModuleAccess(
        "venues", "Venues", "venues.index", "Resources",
        "VENUE", {"CLERK": frozenset("R"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "academic_staff", "Academic staff", "academic_staff.index", "People",
        "ACADEMIC_STAFF_MEMBER", {"DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "departments", "Departments", "departments.index", "Organization",
        "DEPARTMENT", {"HOD": frozenset("RU"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "degrees", "Degrees", "degrees.index", "Organization",
        "DEGREE", {"HOD": frozenset("RU"), "DEAN": frozenset("R")},
    ),
    ModuleAccess(
        "moderators", "Moderators", "moderators.index", "People",
        "MODERATOR", {"DEAN": frozenset("R")},
    ),
)


def has_permission(role, module, action):
    access = next((item for item in MODULE_ACCESS if item.slug == module), None)
    return bool(access and action.upper() in access.actions.get(role, ()))


def actions_for(role, module):
    access = next((item for item in MODULE_ACCESS if item.slug == module), None)
    return access.actions.get(role, frozenset()) if access else frozenset()


def navigation_for(role):
    if not role:
        return []
    return [
        {
            "label": item.title,
            "endpoint": item.endpoint,
            "group": item.group,
        }
        for item in MODULE_ACCESS
        if has_permission(role, item.slug, "R")
    ]
