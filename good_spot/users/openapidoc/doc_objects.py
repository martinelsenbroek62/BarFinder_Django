user_response = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'example': 1
        },
        'first_name': {
            'type': 'string',
            'example': 'Johnny'
        },
        'last_name': {
            'type': 'string',
            'example': 'Raw'
        },
        'email': {
            'type': 'string',
            'example': 'johnny@example.com'
        },
        'image': {
            'type': 'string',
            'example': 'https://example.com/image.jpg'
        },
        'get_thumb': {
            'type': 'string',
            'example': 'https://example.com/image-thumb.jpg'
        },
        'occupation_choices': {
            'type': 'object',
            'example': {
                '1': 'student',
                '2': 'employee'
            }
        },
        'occupation': {
            'type': 'integer',
            'description': '1 - student. 2 - employee.',
            'example': 1
        },
        'occupation_details': {
            'type': 'string',
            'example': 'Taras Shevchenko National University of Kyiv'
        },
        'birthdate': {
            'type': 'string',
            'example': '1987-01-02'
        },
        'city': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'example': '1'
                },
                'name': {
                    'type': 'string',
                    'example': 'Paris'
                }
            }
        },
        'go_out_days': {
            'type': 'array',
            'description': '0 - Monday, 6 - Sunday',
            'example': [4, 5, 6],
            'items': {
                'type': 'integer'
            },
        },
        'favorite_place_types': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'example': [
                {
                    "id": 1,
                    "name": "Night Club",
                    "slug": "night_club",
                    "is_default": False,
                    "is_selected": False
                },
                {
                    "id": 3,
                    "name": "Restaurant",
                    "slug": "restaurant",
                    "is_default": False,
                    "is_selected": True
                }
            ]
        },
        'favorites': {
            'type': 'array',
            'items': {
                'type': 'object'
            },
            'example': [
                {
                    "id": 24,
                    "name": "Style of music",
                    "options": [
                        {
                            "id": 90,
                            "option": "Latino",
                            "is_selected": True
                        },
                        {
                            "id": 89,
                            "option": "Rap and R&B",
                            "is_selected": False
                        },
                        {
                            "id": 87,
                            "option": "Techno",
                            "is_selected": False
                        },
                        {
                            "id": 88,
                            "option": "Various Hits",
                            "is_selected": False
                        }
                    ]
                }
            ]
        }
    }
}

token_response = {
    'type': 'object',
    'properties': {
        'key': {
            'type': 'string',
            'example': 'b5a41b7f2e7e17f521652f2c2fb7fe15a192fbcd'
        },
        'user_id': {
            'type': 'integer',
            'example': 1
        }
    }
}

user_patch_data = {
    'type': 'object',
    'properties': {
        'first_name': {
            'type': 'string',
            'example': 'John'
        },
        'last_name': {
            'type': 'string',
            'example': 'Doe'
        },
        'city': {
            'type': 'integer',
            'example': 2
        },
        'email': {
            'type': 'string',
            'example': 'john@example.com'
        },
        'occupation': {
            'type': 'integer',
            'example': 1
        },
        'occupation_details': {
            'type': 'string',
            'example': 'Name of company'
        },
        'birthdate': {
            'type': 'string',
            'example': '2000-01-01'
        },
        'go_out_days': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'example': [1, 2]
        },
        'favorite_place_types': {
            'type': 'array',
            'items': {
                'type': 'integer'
            },
            'example': [3, 4]
        },
        'favorites': {
            'type': 'array',
            'items': {
                'type': 'object'
            },
            'example': [
                {
                    "id": 24,
                    "options": [90, 100]
                }
            ]
        }
    }
}
