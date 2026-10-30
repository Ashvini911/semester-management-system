from flask import Blueprint, render_template, session

from app.database.connection import query
from app.services.permission_service import MODULE_ACCESS, has_permission
from app.utils.decorators import login_required


bp = Blueprint("dashboard", __name__)


@bp.get("/")
@login_required
def index():
    role = session["role"]
    cards = []
    for module in MODULE_ACCESS:
        if not has_permission(role, module.slug, "R"):
            continue
        total = query(f"SELECT COUNT(*) AS total FROM `{module.table}`")[0]["total"]
        cards.append(
            {
                "title": module.title,
                "count": total,
                "endpoint": module.endpoint,
            }
        )

    upcoming_exams = []
    if has_permission(role, "examinations", "R"):
        upcoming_exams = query(
            "SELECT e.Course_Code, c.Course_Name, e.`Type`, e.`Date`, e.`Time` "
            "FROM EXAM e JOIN COURSE c ON c.Course_Code = e.Course_Code "
            "WHERE e.`Date` >= CURDATE() "
            "ORDER BY e.`Date`, e.`Time` LIMIT 5"
        )
    return render_template(
        "dashboard/index.html",
        cards=cards,
        upcoming_exams=upcoming_exams,
        first_name=session.get("name", ""),
        role=role,
    )
