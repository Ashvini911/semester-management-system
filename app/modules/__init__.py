from app.modules.academic_staff.routes import bp as academic_staff_bp
from app.modules.courses.routes import bp as courses_bp
from app.modules.degrees.routes import bp as degrees_bp
from app.modules.departments.routes import bp as departments_bp
from app.modules.examinations.routes import bp as examinations_bp
from app.modules.lectures.routes import bp as lectures_bp
from app.modules.moderators.routes import bp as moderators_bp
from app.modules.semesters.routes import bp as semesters_bp
from app.modules.timetables.routes import bp as timetables_bp
from app.modules.venues.routes import bp as venues_bp


BLUEPRINTS = (
    semesters_bp,
    courses_bp,
    timetables_bp,
    examinations_bp,
    lectures_bp,
    venues_bp,
    academic_staff_bp,
    departments_bp,
    degrees_bp,
    moderators_bp,
)
