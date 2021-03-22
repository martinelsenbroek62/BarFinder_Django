place_schema_add = {
    "google_place_id": {
        "type": "string",
        "headerTemplate": "Google Place ID",
        "description": "identificator of place"
    },
    "is_published": {
        "type": "boolean",
        "format": "checkbox",
        "default": "true"
    },
    "update_populartimes": {
        "type": "boolean",
        "format": "checkbox",
        "default": "true"
    }
}

updating_rules_schema_items = {
    "type": "object",
    "properties": {
        "day": {
            "type": "string",
            "enum": [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6"
            ],
            "options": {
                'enum_titles': [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday"
                ]
            }
        },
        "time": {
            "type": "string"
        }
    }
}
