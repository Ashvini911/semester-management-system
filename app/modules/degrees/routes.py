from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="degrees",
        title="Degrees",
        table="DEGREE",
        key="Degree_Name",
        fields=(
            FormField("Degree_Name", "Degree name", max_length=100, readonly=True),
            FormField("Credit", "Credits", kind="number", minimum=1, maximum=32767),
            FormField("Duration", "Duration (years)", kind="number", minimum=1, maximum=127),
            FormField(
                "Dep_Name",
                "Department",
                lookup_sql="SELECT Dep_Name AS value, Dep_Name AS label FROM DEPARTMENT ORDER BY Dep_Name",
                lookup_value="value",
            ),
        ),
        list_sql="SELECT d.Degree_Name, d.Credit, d.Duration, d.Dep_Name FROM DEGREE d ORDER BY d.Degree_Name",
        columns=(
            ("Degree_Name", "Degree"),
            ("Credit", "Credits"),
            ("Duration", "Duration"),
            ("Dep_Name", "Department"),
        ),
        search_columns=("d.Degree_Name", "d.Dep_Name"),
    )
)
