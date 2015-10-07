__author__ = 'Carlos'

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.utils.translation import ugettext as _
from principal.services import PeticionCitaService
from principal.models import Profesor
from principal.forms import PeticionCitaForm
from principal.models import Peticioncita
from django.shortcuts import get_object_or_404
from principal.models import Tutoria
from django.contrib import messages
from principal.forms import TutorialForm
from principal.services import TutorialService
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
import datetime
import time
from calendar import timegm


@login_required
def view_tutorials(request, lecturer_id=None, tutorial_id=None):
    if request.method == 'POST':
        lecturer = Profesor.objects.get(id=request.user.id)
        form = TutorialForm(request.POST, lecturer_id=lecturer.id)
        if form.is_valid():
            # Lecturer as parameter (lecturer_id is in the form, but this way we save one DB query)
            TutorialService.update(form, lecturer)
            messages.success(request, _('Tutorial was updated successfully') if form.cleaned_data['tutorial_id'] else _(
                'Tutorial was added successfully.'))
            return HttpResponseRedirect('/lecturer/details/')
    else:
        lecturer = get_object_or_404(Profesor, id=lecturer_id if lecturer_id else request.user.id)
        initial_data = {}
        if request.user.has_perm('principal.profesor'):
            # Edit tutorial
            if tutorial_id:
                tutorial_to_edit = get_object_or_404(Tutoria, id=tutorial_id)

                if not tutorial_to_edit.profesor == lecturer:
                    messages.warning(request, _('You cannot edit this tutorial.'))
                else:
                    initial_data['tutorial_id'] = tutorial_to_edit.id
                    initial_data['start_hour'] = tutorial_to_edit.horainicio.strftime('%H:%M')
                    initial_data['finish_hour'] = tutorial_to_edit.horafin.strftime('%H:%M')
                    initial_data['day'] = tutorial_to_edit.dia

        form = TutorialForm(lecturer_id=request.user.id, initial=initial_data)

    return render_to_response('lecturer/details.html', {'lecturer': lecturer, 'form': form},
                              context_instance=RequestContext(request))


@permission_required('principal.alumno')
def create_tutorial(request):
    if request.method == 'POST':
        student_id = request.user.alumno.id
        form = PeticionCitaForm(request.POST)
        if form.is_valid():
            tutorial_request = PeticionCitaService.create(form, student_id)

            # Business rule: a student cannot request more than two appointments for the same lecturer and day.
            appointment_date = tutorial_request.fechacita.date()
            appointment_day = appointment_date.day
            appointment_month = appointment_date.month
            appointment_year = appointment_date.year

            parameters = [appointment_year, appointment_month, appointment_day, tutorial_request.profesor.id,
                          tutorial_request.alumno.id]

            query = '''SELECT idcita FROM peticioncita
                      WHERE YEAR(fechaCita)=%s AND MONTH(fechaCita)=%s
                      AND DAY(fechaCita)=%s AND profesor=%s AND alumno=%s'''

            same_day_same_lecturer = len(list(Peticioncita.objects.raw(query, parameters)))

            if same_day_same_lecturer < 2:
                tutorial_request.save()
                messages.add_message(request, messages.SUCCESS, _('The request has been sent successfully.'))
                return HttpResponseRedirect('/student/tutorial/create/')
            else:
                messages.add_message(request, messages.ERROR, _(
                    'Sorry, but you cannot request more than two appointments for the same teacher in the same day.'))
    else:
        form = PeticionCitaForm()

    return render_to_response('tutorial/edit.html', {'form': form}, context_instance=RequestContext(request))


# def edit_tutorial(request, tutorial_id):
#     if request.method == 'POST':
#         pass
#     else:
#         form = TutorialForm


@permission_required('principal.profesor')
def delete_tutorial(request, tutorial_id):
    tutorial = Tutoria.objects.get(id=tutorial_id, profesor__id=request.user.id)
    tutorial.delete()
    messages.success(request, _('The tutorial has been removed.'))

    return HttpResponseRedirect('/lecturer/details/')


@permission_required('principal.profesor')
def enable_tutorials(request):
    if request.method == 'POST':
        lecturer = Profesor.objects.get(id=request.user.id)
        TutorialService.enable_tutorials(lecturer)
        messages.add_message(request, messages.SUCCESS, _('Tutorials have been enabled.'))

    return HttpResponseRedirect(request.POST['return_url'])


@permission_required('principal.profesor')
def disable_tutorials(request):
    if request.method == 'POST':
        lecturer = Profesor.objects.get(id=request.user.id)
        motivation = request.POST['motivation']
        add_error = False

        if motivation:
            if not motivation.isspace() and not '' == motivation:
                TutorialService.disable_tutorials(lecturer, motivation)
                messages.success(request, _('Tutorials have been disabled.'))
            else:
                add_error = True
        else:
            add_error = True

        if add_error:
            messages.error(request, _('You must enter a reason to disable tutorials.'))

    return HttpResponseRedirect(request.POST['return_url'])


@permission_required('principal.profesor')
def tutorials_json(request, timestamp_from, timestamp_to, utc_offset):
    lecturer = Profesor.objects.get(id=request.user.id)

    start_date = datetime.datetime.fromtimestamp(int(timestamp_from) / 1000)
    end_date = datetime.datetime.fromtimestamp(int(timestamp_to) / 1000)

    tutorial_requests = lecturer.peticioncita_set.filter(estado='AC', fechacita__gte=start_date,
                                                         fechacita__lt=end_date)
    tutorials = []
    for tutorial_request in tutorial_requests:
        title = str(tutorial_request)
        iso_string = tutorial_request.fechacita.strftime('%Y-%m-%dT%H:%M:%S')
        iso_string_end = tutorial_request.fechacitafin.strftime('%Y-%m-%dT%H:%M:%S')
        timestamp = timegm(
            time.strptime(
                iso_string,
                '%Y-%m-%dT%H:%M:%S'
            )
        )* 1000

        end_timestamp = timegm(
            time.strptime(
                iso_string_end,
                '%Y-%m-%dT%H:%M:%S'
            )
        ) *1000

        completename = tutorial_request.alumno.first_name + ' ' + tutorial_request.alumno.last_name

        tutorials.append({'title': title, "start": timestamp, 'end':end_timestamp, 'short_title': completename, 'motivation':tutorial_request.motivo})

    to_dump = {'success': 1, 'result': tutorials}

    return JsonResponse(to_dump, safe=False)
