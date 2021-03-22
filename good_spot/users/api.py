from django.db.models import Case, When, IntegerField
from rest_framework import mixins, viewsets, generics
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from cities_light.models import City

from good_spot.users import serializers as users_serializers
from good_spot.users import models as users_models
from good_spot.users.openapidoc import documentation
from good_spot.users.permissions import IsOwnerPermission


class FacebookLogin(
    documentation.FacebookLoginJsonSchema,
    SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  documentation.UserViewSetJsonSchema,
                  viewsets.GenericViewSet):
    queryset = users_models.User.objects.all()
    serializer_class = users_serializers.UserModelSerializer
    permission_classes = (IsAuthenticated, IsOwnerPermission)


class SearchCityFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        qs = super(SearchCityFilter, self).filter_queryset(request, queryset, view)
        if self.get_search_terms(request):
            qs = qs.annotate(
                priority=Case(
                    When(
                        name__istartswith=self.get_search_terms(request)[0], then=1
                    ),
                    default=0,
                    output_field=IntegerField()
                )
            ).order_by('-priority')
        return qs


class SearchCityListAPIView(generics.ListAPIView):
    queryset = City.objects.select_related('country')
    serializer_class = users_serializers.SearchCitySerializer
    filter_backends = (SearchCityFilter,)
    search_fields = ('^name', '^alternate_names')
