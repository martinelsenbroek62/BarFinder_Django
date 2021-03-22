from rest_framework import mixins, viewsets
from good_spot.pages import models as pages_models
from good_spot.pages import serializers as pages_serializers


class PageViewSet(mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    Model "Page" is used for storing pages such as Privacy Policy, Terms and Conditions, etc.
    Use slag "terms" to get Terms and Conditions.
    Use slag "policy" to get Privacy Policy.
    """
    serializer_class = pages_serializers.PageModelSerializer
    queryset = pages_models.Page.objects.filter(is_published=True)
    lookup_field = 'slug'
