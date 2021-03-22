from allauth.account.models import EmailAddress
from django.contrib import admin

admin.site.unregister(EmailAddress)
