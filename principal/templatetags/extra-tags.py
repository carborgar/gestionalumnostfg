# -*- coding: utf-8 -*-
from django import template
from django.contrib import messages
from django.utils.translation import ugettext as _
import datetime
import calendar
from django.utils.translation import ugettext_lazy as _

register = template.Library()

label_values = {'EC': 'label label-primary', 'DE': 'label label-danger', 'CA': 'label label-danger',
                'AC': 'label label-success'}


@register.simple_tag(name='display_errors', takes_context=True)
def display_errors(context, form):
    request = context['request']

    if not form.errors:
        return ''

    messages.error(request, _('You have errors in your form. Please, fix them and retry.'))

    html = '<div class="alert alert-dismissible alert-danger" id="form-errors"><dl class="dl-horizontal">'

    for field in form:
        if field.errors:
            html += '<dt>%s' % field.label.encode('utf-8')
            for error in field.errors:
                html += '<dd>%s</dd>' % error.encode('utf-8')
            html += '</dt>'
    html += '</dl></div>'

    return html


@register.simple_tag(name='request_label')
def request_label(tutorial_request):
    return label_values[tutorial_request.estado]


@register.filter()
def abbr(string):
    # Exclude words less than 3 characters (of, del, a, la...)
    return "".join(e[0].upper() for e in string.split() if len(e) > 3)


@register.filter()
def time_intervals(minutes):
    times = []
    for i in range(0, 24 * 4):
        datetime_to_add = (datetime.datetime.combine(datetime.date.today(), datetime.time()) + datetime.timedelta(
            minutes=minutes) * i).time()

        if datetime_to_add not in times:
            times.append(datetime_to_add)

    return times


@register.filter(name='contains_hour')
def contains_hour(tutorials, hour):
    times = [(tut.horainicio, tut.horafin) for tut in tutorials]
    for time in times:
        if time[0] <= hour <= time[1]:
            return True
    return False

@register.filter
def day_name(day_num):
    return _(calendar.day_name[day_num-1])