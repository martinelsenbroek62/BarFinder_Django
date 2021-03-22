import datetime

from django import template
from schedule.models import Calendar
from schedule.settings import CHECK_EVENT_PERM_FUNC, CHECK_CALENDAR_PERM_FUNC
from schedule.templatetags.scheduletags import _cook_slots

from good_spot.places.tasks import get_places_to_update

register = template.Library()


@register.inclusion_tag('proxy/templatetags/_updates_count.html', takes_context=True)
def updates_count(context, slot):
    context['count'] = get_places_to_update(slot.start, slot.end).count()
    return context


@register.inclusion_tag('schedule/_daily_table.html', takes_context=True)
def custom_daily_table(context, day, start=8, end=20, increment=30):
    """
      Display a nice table with occurrences and action buttons.
      Arguments:
      start - hour at which the day starts
      end - hour at which the day ends
      increment - size of a time slot (in minutes)
    """
    user = context['request'].user
    addable = CHECK_EVENT_PERM_FUNC(None, user)
    if 'calendar' in context:
        addable = addable and CHECK_CALENDAR_PERM_FUNC(context['calendar'], user)
    context['addable'] = addable
    day_part = day.get_time_slot(day.start + datetime.timedelta(hours=start), day.start + datetime.timedelta(hours=end))
    # get slots to display on the left
    slots = _cook_slots(day_part, increment)
    context['slots'] = slots
    return context


@register.inclusion_tag('proxy/templatetags/calendar_list.html')
def calendars_list():
    calendars = Calendar.objects.all()
    context = {
        "calendars": calendars
    }
    return context
