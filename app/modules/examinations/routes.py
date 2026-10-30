from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="examinations",
        title="Examinations",
        table="EXAM",
        key="Exam_ID",
        fields=(
            FormField(
                "Semester_ID",
                "Semester",
                lookup_sql="SELECT Semester_ID AS value, Semester_ID AS label FROM SEMESTER ORDER BY Semester_ID",
                lookup_value="value",
            ),
            FormField(
                "Course_Code",
                "Course",
                lookup_sql="SELECT Course_Code AS value, CONCAT(Course_Code, ' - ', Course_Name) AS label FROM COURSE ORDER BY Course_Code",
                lookup_value="value",
                lookup_label="label",
            ),
            FormField("Type", "Examination type", max_length=30),
            FormField("Date", "Date", kind="date"),
            FormField("Time", "Time", kind="time"),
        ),
        list_sql=(
            "SELECT e.Exam_ID, e.Semester_ID, e.Course_Code, c.Course_Name, "
            "e.`Type`, e.`Date`, e.`Time` FROM EXAM e "
            "JOIN COURSE c ON c.Course_Code = e.Course_Code "
            "ORDER BY e.`Date`, e.`Time`"
        ),
        columns=(
            ("Exam_ID", "ID"),
            ("Semester_ID", "Semester"),
            ("Course_Code", "Course code"),
            ("Course_Name", "Course"),
            ("Type", "Type"),
            ("Date", "Date"),
            ("Time", "Time"),
        ),
        search_columns=("e.Semester_ID", "e.Course_Code", "c.Course_Name", "e.`Type`"),
    )
)
