from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="timetables",
        title="Timetables",
        table="TIME_TABLE",
        key="Timetable_ID",
        fields=(
            FormField(
                "Semester_ID",
                "Semester",
                lookup_sql="SELECT Semester_ID AS value, Semester_ID AS label FROM SEMESTER ORDER BY Semester_ID",
                lookup_value="value",
            ),
            FormField("Year", "Academic year", max_length=9),
            FormField("Place", "Place", required=False, max_length=100),
        ),
        list_sql=(
            "SELECT t.Timetable_ID, t.Semester_ID, t.`Year`, t.Place "
            "FROM TIME_TABLE t ORDER BY t.`Year` DESC, t.Timetable_ID"
        ),
        columns=(
            ("Timetable_ID", "ID"),
            ("Semester_ID", "Semester"),
            ("Year", "Academic year"),
            ("Place", "Place"),
        ),
        search_columns=("t.Semester_ID", "t.`Year`", "t.Place"),
    )
)
