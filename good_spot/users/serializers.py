from cities_light.models import City
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.db.models import Case, When, BooleanField
from django.utils.translation import ugettext as _
from rest_auth.registration.serializers import RegisterSerializer
from rest_auth.serializers import PasswordChangeSerializer, PasswordResetSerializer, LoginSerializer
from rest_auth.models import TokenModel
from rest_framework import serializers, exceptions
from good_spot.places import serializers as places_serializers
from good_spot.filter import serializers as filter_serializers
from good_spot.users import models as users_models
from good_spot.places import models as places_models
from good_spot.filter import models as filter_models

try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email, send_email_confirmation
except ImportError:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")

# Get the UserModel
UserModel = get_user_model()


class UserModelSerializer(serializers.ModelSerializer):
    favorite_place_types = serializers.PrimaryKeyRelatedField(
        queryset=places_models.PlaceType.objects.all(),
        many=True
    )
    favorites = serializers.SerializerMethodField()
    get_thumb = serializers.ReadOnlyField()
    has_password = serializers.SerializerMethodField()

    class Meta:
        model = users_models.User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'image',
            'get_thumb',
            'occupation',
            'occupation_details',
            'birthdate',
            'city',
            'go_out_days',
            'favorite_place_types',
            'favorites',
            'has_password'
        )

    def validate_go_out_days(self, value):
        if len(value) > len(set(value)):
            raise serializers.ValidationError(_('Days for going out should be unique.'))
        return value

    def validate_favorites(self, value):
        # TODO validate favorites
        return value

    def validate(self, attrs):
        try:
            user = self.context['request'].user
        except Exception as e:
            raise serializers.ValidationError(_('User does not represent in request.'))
        if self.initial_data.get('favorites', None):
            favorites = self.validate_favorites(self.initial_data['favorites'])

            for fav in favorites:

                fav_options = users_models.FavoriteChoiceFilterField.objects.filter(
                    user=user,
                    filter_field_id=fav['id']
                ).first()
                if not fav_options:
                    fav_options = users_models.FavoriteChoiceFilterField.objects.create(
                        user=user,
                        filter_field_id=fav['id']
                    )
                options_exist = list(fav_options.value.values_list('id', flat=True))

                options_add = list(set(fav['options']) - set(options_exist))
                options_remove = list(set(options_exist) - set(fav['options']))

                fav_options.value.add(*options_add)
                fav_options.value.remove(*options_remove)
        return attrs

    def to_representation(self, instance):
        ret = super(UserModelSerializer, self).to_representation(instance)

        favs = places_models.PlaceType.objects.annotate(
            is_selected=Case(
                When(
                    id__in=list(instance.favorite_place_types.values_list('id', flat=True)), then=True
                ),
                default=False,
                output_field=BooleanField()
            )
        )

        ret['favorite_place_types'] = places_serializers.PlaceTypeAnnotatedSerializer(
            instance=favs, many=True
        ).data

        ret['occupation_choices'] = dict(users_models.OCCUPATION_CHOICES)
        ret['city'] = places_serializers.CitySerializer(
            instance=instance.city
        ).data if instance.city else None

        return ret

    def get_favorites(self, instance):
        filter_fields = filter_models.ChoiceFilterField.objects.filter(is_users_tastes=True)
        serializer = filter_serializers.UserFilterFieldModelSerializer(
            instance=filter_fields,
            many=True,
            context={
                'user': instance
            }
        )
        return serializer.data

    def get_has_password(self, instance):
        return instance.has_usable_password()


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    user_id = serializers.SerializerMethodField()

    class Meta:
        model = TokenModel
        fields = ('key', 'user_id')

    def user_id(self, obj):
        return obj.id


class SearchCitySerializer(serializers.ModelSerializer):
    country = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ('id', 'name', 'country')

    def get_country(self, obj):
        return obj.country.name


class CustomPasswordChangeSerializer(PasswordChangeSerializer):

    def __init__(self, *args, **kwargs):
        user = kwargs['context']['request'].user

        if user.has_usable_password():
            self.old_password_field_enabled = getattr(
                settings, 'OLD_PASSWORD_FIELD_ENABLED', False
            )
        else:
            self.old_password_field_enabled = False

        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError(_('Invalid password'))
        return value


class RegisterSerializer(RegisterSerializer):
    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _('Email is already registered. Please use "Sign in" to connect with this email address'))
        return email


class PasswordResetSerializerCustom(PasswordResetSerializer):

    def validate_email(self, value):
        if not list(PasswordResetForm().get_users(value)):
            raise serializers.ValidationError(_('There is no password linked to this Email address.'))

        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value


class LoginSerializerCustom(LoginSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    # added resending confirmation email
                    send_email_confirmation(self.context['request'], user)
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
