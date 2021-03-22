filter_params = {
    'type': 'object',
    'properties': {
        'city_id': {
            'type': 'integer',
            'description': 'ID of existing city.',
            'example': '2'
        },
        'slug': {
            'type': 'string',
            'description': 'Slug of place\'s type.',
            'example': 'bar'
        },
        'filter': {
            'type': 'array',
            'description': 'If type of filter field is `bool` data should be true or false.<br>'
                           'If type of filter field is `choice` data should be string.<br>'
                           'If type of filter field is `multi` data should be list of option\'s ids.',
            'example': [
                {
                    'id': 1,
                    'options': True,
                },
                {
                    'id': 2,
                    'options': [11, 12]
                },
                {
                    'id': 3,
                    'options': 'Some option'
                }
            ]
        }
    }
}

filter_response = {
    'type': 'object',
    'properties': {

    }
}

filter_errors = {
    'type': 'object',
    'properties': {

    }
}

city_response = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'description': '',
            'example': 1
        },
        'name': {
            'type': 'string',
            'description': 'The name of the city',
            'example': 'Kyiv'
        },
        'country': {
            'type': 'string',
            'description': 'Country',
            'example': 'Ukraine'
        },
        'timezone': {
            'type': 'string',
            'description': '',
            'example': 'Europe/Kiev'
        },
        'latitude': {
            'type': 'float',
            'description': '',
            'example': 50.45466
        },
        'longitude': {
            'type': 'float',
            'description': '',
            'example': 30.5238
        },
        'name_variants': {
            'type': 'array',
            'description': '',
            'example': [
                'Киев',
                'Київ',
                'Kyiv city',
                'Kiev',
                'Kiyev',
                'г. Киев'
            ]
        },
        'current_city': {
            'type': 'string',
            'description': 'Returns `native` or `closest`.',
            'example': 'native'
        },
    }
}

place_type_response = {
    'type': 'array',
    'example': [
        {
            "id": 1,
            "slug": "night_club",
            "name": "Night Club",
            "is_default": True
        },
        {
            "id": 2,
            "slug": "bar",
            "name": "Bar",
            "is_default": False
        }
    ]
}

filter_get_response = {
    'type': 'array',
    'example': [{
        "id": 1,
        "name": "Restaurant",
        "slug": "restaurant",
        "price": [
            1,
            2,
            3,
            4
        ],
        "filters": [
            {
                "id": 11,
                "name": "Restaurant type",
                "field_type": "multi",
                "is_shown_in_short_description": False,
                "options": [
                    {
                        "id": 1,
                        "option": "Asian"
                    },
                    {
                        "id": 2,
                        "option": "Bar-club"
                    },
                    {
                        "id": 3,
                        "option": "Brewery"
                    },
                    {
                        "id": 4,
                        "option": "French",
                    },
                    {
                        "id": 5,
                        "option": "Roof terrace"
                    }
                ]
            },
            {
                "id": 33,
                "name": "Pre-party spots",
                "field_type": "bool",
                "is_shown_in_short_description": True,
                "options": None
            }
        ]
    }]
}

place_object_example = {
    "id": 143,
    "name": "Castel",
    "features": "null",
    "short_description": "null",
    "about_place": [],
    "google_place_id": "ChIJ-Z0Zktlx5kcR-icm_fX-aY8",
    "is_gay_friendly": "false",
    "place_types": [
        {
            "id": 3,
            "name": "Restaurant",
            "slug": "restaurant",
            "is_default": "false"
        },
        {
            "id": 1,
            "name": "Night Club",
            "slug": "night_club",
            "is_default": "false"
        }
    ],
    "google_rating": 3.6,
    "google_price_level": 4,
    "location": {
        "lat": 48.8520442,
        "lng": 2.3346246
    },
    "address": "15 Rue Princesse, 75006 Paris, France",
    "website": "http://www.castelparis.com/",
    "phone": "+33140515280",
    "long_description": "",
    "special_event": "null",
    "place_fields": {},
    "open_hours": {
        "periods": [
            {
                "open": {
                    "day": 2,
                    "time": "2030"
                },
                "close": {
                    "day": 3,
                    "time": "0200"
                }
            },
            {
                "open": {
                    "day": 3,
                    "time": "2030"
                },
                "close": {
                    "day": 4,
                    "time": "0200"
                }
            },
            {
                "open": {
                    "day": 4,
                    "time": "2030"
                },
                "close": {
                    "day": 5,
                    "time": "0500"
                }
            },
            {
                "open": {
                    "day": 5,
                    "time": "2030"
                },
                "close": {
                    "day": 6,
                    "time": "0500"
                }
            },
            {
                "open": {
                    "day": 6,
                    "time": "2030"
                },
                "close": {
                    "day": 0,
                    "time": "0500"
                }
            }
        ],
        "open_now": "false",
        "weekday_text": [
            "Monday: Closed",
            "Tuesday: 8:30 PM – 2:00 AM",
            "Wednesday: 8:30 PM – 2:00 AM",
            "Thursday: 8:30 PM – 5:00 AM",
            "Friday: 8:30 PM – 5:00 AM",
            "Saturday: 8:30 PM – 5:00 AM",
            "Sunday: Closed"
        ]
    },
    "populartimes": [
        {
            "data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "name": "Monday"
        },
        {
            "data": [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                14,
                25,
                35,
                35
            ],
            "name": "Tuesday"
        },
        {
            "data": [
                25,
                13,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                37,
                59,
                65,
                56
            ],
            "name": "Wednesday"
        },
        {
            "data": [
                42,
                28,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                21,
                48,
                80,
                100
            ],
            "name": "Thursday"
        },
        {
            "data": [
                92,
                63,
                32,
                12,
                7,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                6,
                18,
                27,
                33
            ],
            "name": "Friday"
        },
        {
            "data": [
                49,
                65,
                53,
                26,
                8,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                4,
                17,
                30,
                35
            ],
            "name": "Saturday"
        },
        {
            "data": [
                49,
                69,
                60,
                29,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "name": "Sunday"
        }
    ],
    "place_images_count": 0,
    "place_images": []
}

search_response_objects = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer',
            'description': 'ID the many2many object.',
            'example': 1
        },
        'place': {
            'type': 'object',
            'example': place_object_example
        },
        'place_type': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer',
                    'description': 'ID of place type.',
                    'example': 22
                },
                'name': {
                    'type': 'string',
                    'description': 'Name of place type.',
                    'example': 'Bar'
                }
            }
        }
    }
}

search_response_array = {
    'type': 'array',
    'items': search_response_objects
}
