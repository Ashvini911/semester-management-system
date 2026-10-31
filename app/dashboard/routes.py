from flask import Blueprint, current_app, render_template, session
import mysql.connector

from app.database.connection import query
from app.services.permission_service import MODULE_ACCESS, has_permission
from app.utils.decorators import login_required


bp = Blueprint("dashboard", __name__)


@bp.get("/")
@login_required
def index():
    role = session["role"]
    cards = []
    database_error = False
    for module in MODULE_ACCESS:
        if not has_permission(role, module.slug, "R"):
            continue
        try:
            total = query(f"SELECT COUNT(*) AS total FROM `{module.table}`")[0]["total"]
        except mysql.connector.Error:
            current_app.logger.exception("Dashboard count failed for %s", module.table)
            database_error = True
            total = "–"
        cards.append(
            {
                "title": module.title,
                "count": total,
                "endpoint": module.endpoint,
            }
        )

    upcoming_exams = []
    if has_permission(role, "examinations", "R") and not database_error:
        try:
            upcoming_exams = query(
                "SELECT e.Course_Code, c.Course_Name, e.`Type`, e.`Date`, e.`Time` "
                "FROM EXAM e JOIN COURSE c ON c.Course_Code = e.Course_Code "
                "WHERE e.`Date` >= CURDATE() "
                "ORDER BY e.`Date`, e.`Time` LIMIT 5"
            )
        except mysql.connector.Error:
            current_app.logger.exception("Dashboard exam lookup failed")
            database_error = True
    return render_template(
        "dashboard/index.html",
        database_error=database_error,
        cards=cards,
        upcoming_exams=upcoming_exams,
        first_name=session.get("name", ""),
        role=role,
    )
