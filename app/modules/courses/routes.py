from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="courses",
        title="Courses",
        table="COURSE",
        key="Course_Code",
        fields=(
            FormField("Course_Code", "Course code", max_length=10, readonly=True),
            FormField("Course_Name", "Course name", max_length=100),
            FormField("Credit", "Credits", kind="number", minimum=1, maximum=6),
            FormField(
                "Semester_ID",
                "Semester",
                lookup_sql="SELECT Semester_ID AS value, Semester_ID AS label FROM SEMESTER ORDER BY Semester_ID",
                lookup_value="value",
            ),
        ),
        list_sql=(
            "SELECT c.Course_Code, c.Course_Name, c.Credit, c.Semester_ID, "
            "s.Academic_Year FROM COURSE c "
            "JOIN SEMESTER s ON s.Semester_ID = c.Semester_ID "
            "ORDER BY s.Start_Date DESC, c.Course_Code"
        ),
        columns=(
            ("Course_Code", "Course code"),
            ("Course_Name", "Course name"),
            ("Credit", "Credits"),
            ("Semester_ID", "Semester"),
            ("Academic_Year", "Academic year"),
        ),
        search_columns=("c.Course_Code", "c.Course_Name", "s.Academic_Year"),
    )
)
