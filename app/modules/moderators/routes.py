from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="moderators",
        title="Moderators",
        table="MODERATOR",
        key="Email",
        fields=(
            FormField("Email", "Email", kind="email", max_length=100, readonly=True),
            FormField("First_Name", "First name", max_length=50),
            FormField("Last_Name", "Last name", max_length=50),
            FormField("Contact_No", "Contact number", required=False, max_length=15),
            FormField("Official_Address", "Official address", required=False, max_length=200),
            FormField("Designation", "Designation", required=False, max_length=50),
        ),
        list_sql=(
            "SELECT Email, First_Name, Last_Name, Contact_No, Official_Address, Designation "
            "FROM MODERATOR ORDER BY Last_Name, First_Name"
        ),
        columns=(
            ("Email", "Email"),
            ("First_Name", "First name"),
            ("Last_Name", "Last name"),
            ("Contact_No", "Contact"),
            ("Official_Address", "Address"),
            ("Designation", "Designation"),
        ),
        search_columns=("Email", "First_Name", "Last_Name", "Designation"),
    )
)
