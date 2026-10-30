from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="academic_staff",
        title="Academic staff",
        table="ACADEMIC_STAFF_MEMBER",
        key="Staff_ID",
        fields=(
            FormField("Staff_ID", "Staff ID", max_length=10, readonly=True),
            FormField("First_Name", "First name", max_length=50),
            FormField("Last_Name", "Last name", max_length=50),
            FormField("Email", "Email", kind="email", max_length=100),
            FormField("Contact_No", "Contact number", required=False, max_length=15),
            FormField("Staff_Type", "Staff type", choices=("LECTURER", "VISITING", "INTERNAL")),
            FormField("Employment", "Employment", required=False, choices=("PERMANENT", "TEMPORARY")),
        ),
        list_sql=(
            "SELECT Staff_ID, First_Name, Last_Name, Email, Contact_No, Staff_Type, Employment "
            "FROM ACADEMIC_STAFF_MEMBER ORDER BY Last_Name, First_Name"
        ),
        columns=(
            ("Staff_ID", "Staff ID"),
            ("First_Name", "First name"),
            ("Last_Name", "Last name"),
            ("Email", "Email"),
            ("Contact_No", "Contact"),
            ("Staff_Type", "Type"),
            ("Employment", "Employment"),
        ),
        search_columns=("Staff_ID", "First_Name", "Last_Name", "Email"),
    )
)
