from drf_skd_tools.swagger.schema_views import BaseJsonSchema

from good_spot.common.openapidoc.common_main_objects import main_forbidden_object, main_not_found_object
from good_spot.users.openapidoc import doc_objects


class UserViewSetJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.user_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        },
        'patch': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.user_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }

    parameters_docs = {
        'patch': [{
            'in': 'body',
            'schema': doc_objects.user_patch_data
        }]
    }


class FacebookLoginJsonSchema(BaseJsonSchema):
    responses_docs = {
        'post': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.token_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }
