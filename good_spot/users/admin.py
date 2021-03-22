from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext as _

from . import models as users_models


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = users_models.User


class MyUserCreationForm(UserCreationForm):
    error_message = UserCreationForm.error_messages.update({
        'duplicate_username': 'This username has already been taken.'
    })

    class Meta(UserCreationForm.Meta):
        model = users_models.User

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            users_models.User.objects.get(username=username)
        except users_models.User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


@admin.register(users_models.User)
class UserAdmin(AuthUserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name',
            'last_name',
            'email',
            'image',
            'occupation',
            'occupation_details',
            'birthdate',
            'city',
            'go_out_days',
            'favorite_place_types'
        )}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(users_models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass


@admin.register(users_models.FavoriteChoiceFilterField)
class FavoriteChoiceFilterFieldAdmin(admin.ModelAdmin):
    pass
