from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="semesters",
        title="Semesters",
        table="SEMESTER",
        key="Semester_ID",
        fields=(
            FormField("Semester_ID", "Semester ID", max_length=10, readonly=True),
            FormField("Academic_Year", "Academic year", max_length=9),
            FormField("Start_Date", "Start date", kind="date"),
            FormField("End_Date", "End date", kind="date"),
        ),
        list_sql=(
            "SELECT Semester_ID, Academic_Year, Start_Date, End_Date FROM SEMESTER "
            "ORDER BY Start_Date DESC"
        ),
        columns=(
            ("Semester_ID", "Semester ID"),
            ("Academic_Year", "Academic year"),
            ("Start_Date", "Start date"),
            ("End_Date", "End date"),
        ),
        search_columns=("Semester_ID", "Academic_Year"),
    )
)
