from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="lectures",
        title="Lectures",
        table="LECTURE",
        key="Lecture_ID",
        fields=(
            FormField(
                "Course_Code",
                "Course",
                lookup_sql="SELECT Course_Code AS value, CONCAT(Course_Code, ' - ', Course_Name) AS label FROM COURSE ORDER BY Course_Code",
                lookup_value="value",
                lookup_label="label",
            ),
            FormField(
                "Staff_ID",
                "Lecturer",
                lookup_sql="SELECT Staff_ID AS value, CONCAT(Staff_ID, ' - ', First_Name, ' ', Last_Name) AS label FROM ACADEMIC_STAFF_MEMBER ORDER BY Staff_ID",
                lookup_value="value",
                lookup_label="label",
            ),
            FormField(
                "Venue_No",
                "Venue",
                lookup_sql="SELECT Venue_No AS value, CONCAT(Venue_No, ' - ', Venue_Name) AS label FROM VENUE ORDER BY Venue_No",
                lookup_value="value",
                lookup_label="label",
            ),
            FormField(
                "Moderator_Email",
                "Moderator",
                required=False,
                lookup_sql="SELECT Email AS value, CONCAT(First_Name, ' ', Last_Name, ' - ', Email) AS label FROM MODERATOR ORDER BY Email",
                lookup_value="value",
                lookup_label="label",
            ),
            FormField("Date", "Date", kind="date"),
            FormField("Time", "Time", kind="time"),
            FormField("Mode", "Mode", choices=("Physical", "Online")),
        ),
        list_sql=(
            "SELECT l.Lecture_ID, l.Course_Code, c.Course_Name, "
            "CONCAT(s.First_Name, ' ', s.Last_Name) AS Lecturer, "
            "l.Venue_No, v.Venue_Name, l.`Date`, l.`Time`, l.Mode "
            "FROM LECTURE l JOIN COURSE c ON c.Course_Code = l.Course_Code "
            "JOIN ACADEMIC_STAFF_MEMBER s ON s.Staff_ID = l.Staff_ID "
            "JOIN VENUE v ON v.Venue_No = l.Venue_No "
            "ORDER BY l.`Date` DESC, l.`Time`"
        ),
        columns=(
            ("Lecture_ID", "ID"),
            ("Course_Code", "Course"),
            ("Lecturer", "Lecturer"),
            ("Venue_Name", "Venue"),
            ("Date", "Date"),
            ("Time", "Time"),
            ("Mode", "Mode"),
        ),
        search_columns=("c.Course_Code", "c.Course_Name", "s.First_Name", "s.Last_Name", "v.Venue_Name"),
    )
)
