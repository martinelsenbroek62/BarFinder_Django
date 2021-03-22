$(document).ready(function () {

    var place_calendar = new JSONEditor(
        document.getElementById("place_calendar_holder"),
        {
            schema: {
                title: "Updating calendar",
                type: "array",
                id: "calendar",
                format: "table",
                items: updating_rules_schema_items
            },
            startval: updating_rules_initial,
            show_errors: 'never',
            // disable_array_add: "true",
            // disable_array_delete: true,
            // disable_array_delete_all_rows: true,
            disable_array_delete_last_row: true,
            disable_array_reorder: true
        }
    );

});
