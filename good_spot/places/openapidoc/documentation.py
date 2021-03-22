from drf_skd_tools.swagger.schema_views import BaseJsonSchema

from good_spot.common.openapidoc.common_main_objects import (
    main_unauthorized_object,
    main_forbidden_object,
    main_not_found_object
)
from good_spot.places.openapidoc import doc_objects


class PlaceViewSetJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.'
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }

    parameters_docs = {
        'get': [{
            'in': 'query',
            'name': 'city',
            'description': 'The name of city.',
            'type': 'string',
            'required': False
        }, {
            'in': 'query',
            'name': 'type_id',
            'description': 'The ID of place types.',
            'type': 'integer',
            'required': False
        }, {
            'in': 'path',
            'name': 'id',
            'description': 'The ID of the place.',
            'type': 'integer',
            'required': False
        }]
    }


class CityListAPIViewJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.city_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }

    parameters_docs = {
        'get': [{
            'in': 'query',
            'name': 'lat',
            'description': 'Latitude.',
            'type': 'float',
            'required': False
        }, {
            'in': 'query',
            'name': 'lng',
            'description': 'Longitude.',
            'type': 'float',
            'required': False
        }]
    }


class FilterViewSetJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.filter_get_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        },
        'post': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.filter_get_response
            },
            '400': {
                'description': 'Filter errors.',
                'schema': doc_objects.filter_errors
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }

    parameters_docs = {
        'get': [{
            'in': 'path',
            'name': 'city_id',
            'description': 'The id of city.',
            'type': 'integer',
            'required': False
        }],
        'post': [{
            'in': 'body',
            'name': 'options',
            'description': 'Filtering.',
            'schema': doc_objects.filter_params
        }]
    }


class PlaceTypeViewSetJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.place_type_response
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }


class SearchListAPIViewJsonSchema(BaseJsonSchema):
    responses_docs = {
        'get': {
            '200': {
                'description': 'Success! Request successfully processed.',
                'schema': doc_objects.search_response_array
            },
            '403': main_forbidden_object,
            '404': main_not_found_object
        }
    }

    parameters_docs = {
        'get': [{
            'in': 'path',
            'name': 'name',
            'description': 'Input part of the name of place.',
            'type': 'string',
            'required': False
        }, {
            'in': 'path',
            'name': 'city_id',
            'description': 'Input ID of city.',
            'type': 'integer',
            'required': False
        }]
    }
