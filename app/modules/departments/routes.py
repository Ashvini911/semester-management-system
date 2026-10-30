from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="departments",
        title="Departments",
        table="DEPARTMENT",
        key="Dep_Name",
        fields=(
            FormField("Dep_Name", "Department name", max_length=100, readonly=True),
            FormField(
                "Email",
                "Head of department",
                lookup_sql="SELECT Email AS value, Email AS label FROM HOD ORDER BY Email",
                lookup_value="value",
            ),
        ),
        list_sql="SELECT Dep_Name, Email FROM DEPARTMENT ORDER BY Dep_Name",
        columns=(("Dep_Name", "Department"), ("Email", "HOD email")),
        search_columns=("Dep_Name", "Email"),
    )
)
