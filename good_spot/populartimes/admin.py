from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

from good_spot.populartimes.models import Populartimes


@admin.register(Populartimes)
class PopulartimesAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})}
    }
