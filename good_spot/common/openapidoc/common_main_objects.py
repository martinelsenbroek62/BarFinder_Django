main_forbidden_object = {
    'description': 'Forbidden',
    'schema': {
        'type': 'object',
        'properties': {
            'detail': {
                'type': 'string',
                'description': '',
                'example': 'You do not have permission to perform this action.'
            }
        }
    },
}

main_unauthorized_object = {
    'description': 'Unauthorized',
    'schema': {
        'type': 'object',
        'properties': {
            'detail': {
                'type': 'string',
                'description': '',
                'example': 'Authentication credentials were not provided.'
            }
        }
    },
}

main_not_found_object = {
    'description': 'Not Found',
    'schema': {
        'type': 'object',
        'properties': {
            'detail': {
                'type': 'string',
                'description': '',
                'example': 'Not found.'
            }
        }
    },
}
