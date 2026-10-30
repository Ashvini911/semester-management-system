from app.modules.crud import FormField, ModuleSpec, create_crud_blueprint


bp = create_crud_blueprint(
    ModuleSpec(
        slug="venues",
        title="Venues",
        table="VENUE",
        key="Venue_No",
        fields=(
            FormField("Venue_No", "Venue number", max_length=10, readonly=True),
            FormField("Venue_Name", "Venue name", max_length=100),
            FormField("Capacity", "Capacity", kind="number", minimum=1, maximum=32767),
            FormField("Floor", "Floor", kind="number", required=False, minimum=-128, maximum=127),
            FormField("Building", "Building", required=False, max_length=50),
            FormField("Venue_Type", "Venue type", choices=("LAB", "LECTURE_HALL")),
        ),
        list_sql=(
            "SELECT Venue_No, Venue_Name, Capacity, Floor, Building, Venue_Type "
            "FROM VENUE ORDER BY Building, Floor, Venue_Name"
        ),
        columns=(
            ("Venue_No", "Venue number"),
            ("Venue_Name", "Venue"),
            ("Capacity", "Capacity"),
            ("Floor", "Floor"),
            ("Building", "Building"),
            ("Venue_Type", "Type"),
        ),
        search_columns=("Venue_No", "Venue_Name", "Building"),
    )
)
