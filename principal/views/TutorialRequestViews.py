# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required, login_required
from principal.models import Peticioncita, Profesor, Alumno
from django.shortcuts import render_to_response
from django.template import RequestContext
from principal.services import PeticionCitaService, LecturerService
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from principal.forms import DenyRequestForm
import time
from principal.forms import RejectAcceptedTutorialsForm
from time import mktime
import datetime
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404
from principal.forms import TutorialRequestForm, AutoAsignTutorialForm
from principal.views import EmailViews
import hashlib


@permission_required('principal.profesor')
def view_requests(request):
    if request.method == 'POST':
        form = DenyRequestForm(request.POST, lecturer_id=request.user.id)
        if form.is_valid():
            PeticionCitaService.cancel(form)
            messages.success(request, _('Request was rejected successfully.'))
    else:
        form = DenyRequestForm(lecturer_id=request.user.id)

    tutorial_requests = PeticionCitaService.lecturer_requests(request.user.id, 'EC')

    return render_to_response('tutorial_request/list.html',
                              {'tutorial_requests': tutorial_requests, 'form': form, 'title': _('Tutorial requests')},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def accept_request(request, tutorial_request_id):
    tutorial_request = Peticioncita.objects.get(idcita=tutorial_request_id)
    lecturer = Profesor.objects.get(id=request.user.id)

    assert lecturer == tutorial_request.profesor

    if PeticionCitaService.can_accept(tutorial_request):
        PeticionCitaService.accept(tutorial_request)
        EmailViews.send_tutorial_accepted_mail(tutorial_request)
        messages.success(request, _('Request was accepted successfully.'))
    else:
        messages.warning(request, _('There is another accepted request for this date. The request was not accepted.'))

    return HttpResponseRedirect('/lecturer/tutorialRequest/list')


@permission_required('principal.view_tutorial_request_list')
def accepted_requests(request):
    if request.method == 'POST':
        form = RejectAcceptedTutorialsForm(request.POST, lecturer_id=request.user.id)
        if form.is_valid():
            messages.success(request, _('Tutorials was cancelled successfully.'))
            PeticionCitaService.cancel_all(form.cleaned_data['tutorial_requests'], form.cleaned_data['motivation'])
            return HttpResponseRedirect('/tutorialRequest/accepted')

    if request.user.has_perm('principal.alumno'):
        tutorial_requests = PeticionCitaService.student_requests(request.user.id, 'AC')
        form = None
    else:
        tutorial_requests = PeticionCitaService.lecturer_requests(request.user.id, 'AC')
        form = None
        if request.method == 'GET':
            form = RejectAcceptedTutorialsForm(lecturer_id=request.user.id)

    template_vars = {'tutorial_requests': tutorial_requests, 'title': _('Accepted requests'),
                     'reject_form': form}

    return render_to_response('tutorial_request/list.html', template_vars, context_instance=RequestContext(request))


@permission_required('principal.alumno')
def student_all_requests(request):
    tutorial_requests = PeticionCitaService.student_requests(request.user.id)

    return render_to_response('tutorial_request/list.html',
                              {'tutorial_requests': tutorial_requests, 'title': _('Tutorial requests')},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def tutorial_calendar(request):
    return render_to_response('calendar.html', context_instance=RequestContext(request))


@permission_required('principal.alumno')
def seek_tutorial(request, lecturer_id):
    lecturer = get_object_or_404(Profesor, id=lecturer_id)

    if request.method == 'POST':
        form = TutorialRequestForm(request.POST)
        if form.is_valid():
            tutorial_request = PeticionCitaService.create(form, request.user.id)

            if PeticionCitaService.can_request(tutorial_request):
                tutorial_request.save()
                EmailViews.send_tutorial_request_mail(request, tutorial_request)
                messages.add_message(request, messages.SUCCESS, _('The request has been sent successfully.'))

                return HttpResponseRedirect('/student/tutorial/seek/%s' % lecturer_id)
            else:
                messages.add_message(request, messages.ERROR, _(
                    'Sorry, but you cannot request more than two appointments for the same teacher in the same day.'))

    else:
        form = TutorialRequestForm(initial={'lecturer': lecturer.id})

    return render_to_response('tutorial_request/calendar.html', {'lecturer': lecturer, 'form': form},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def auto_assign_tutorial(request):
    lecturer = Profesor.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = AutoAsignTutorialForm(request.POST)
        if form.is_valid():
            tutorial_request = PeticionCitaService.auto_assign(form, lecturer)
            PeticionCitaService.cancel_concurrent_requests(tutorial_request)
            messages.add_message(request, messages.SUCCESS, _('Tutorial assigned successfully.'))

            return HttpResponseRedirect('/lecturer/tutorial/assign')

    else:
        form = AutoAsignTutorialForm()

    return render_to_response('tutorial_request/calendar.html', {'lecturer': lecturer, 'form': form},
                              context_instance=RequestContext(request))


@login_required()
def tutorials_json(request):
    start = datetime.datetime.fromtimestamp(mktime(time.strptime(request.GET['start'], '%Y-%m-%d')))
    lecturer_id = request.GET['lecturer_id']

    prof = get_object_or_404(Profesor, id=lecturer_id)
    tutorials_json = []
    hour_intervals = time_intervals(30)

    for i in range(1, 6):
        day_tutorials = prof.tutoria_set.filter(dia=i)
        query = '''SELECT idCita FROM peticioncita
                      WHERE estado=%s AND YEAR(fechaCita)=%s AND MONTH(fechaCita)=%s
                      AND DAY(fechaCita)=%s AND profesor=%s'''

        accepted_parameters = ['AC']
        queued_parameters = ['EC']

        common_parameters = [int(start.year), int(start.month), int(start.day), prof.id]

        accepted_parameters += common_parameters
        queued_parameters += common_parameters

        day_accepted_tutorials = [Peticioncita.objects.get(idcita=pet_id.idcita) for pet_id in
                                  list(Peticioncita.objects.raw(query, accepted_parameters))]

        day_queued_tutorials = [Peticioncita.objects.get(idcita=pet_id.idcita) for pet_id in
                                list(Peticioncita.objects.raw(query, queued_parameters))]

        for interval in hour_intervals:
            # Comprobar si hay tutorias en esa hora
            tutorial = check_tutorials(day_tutorials, interval)
            if tutorial:
                # Hay tutorias -> comprobar si hay una cita que empiece en el intervalo
                accepted_tutorial = check_match(interval, day_accepted_tutorials)
                queued_tutorial = check_match(interval, day_queued_tutorials)
                print(queued_tutorial)
                if accepted_tutorial:
                    # Sí -> evento en rojo
                    start_accepted = start.replace(hour=accepted_tutorial.fechacita.time().hour,
                                                   minute=accepted_tutorial.fechacita.time().minute)
                    end_accepted = start.replace(hour=accepted_tutorial.fechacitafin.time().hour,
                                                 minute=accepted_tutorial.fechacitafin.time().minute)

                    tutorials_json.append(
                        {'title': _('Busy'), 'start': start_accepted, 'end': end_accepted, 'backgroundColor': 'red'})
                    start = end_accepted

                elif queued_tutorial:
                    # Evento amarillo
                    start_queued = start.replace(hour=queued_tutorial.fechacita.time().hour,
                                                 minute=queued_tutorial.fechacita.time().minute)
                    end_queued = start.replace(hour=queued_tutorial.fechacitafin.time().hour,
                                               minute=queued_tutorial.fechacitafin.time().minute)

                    tutorials_json.append({'title': _('Available'), 'start': start_queued, 'end': end_queued,
                                           'backgroundColor': 'orange', 'className': 'tutorial-warning'})
                    start = end_queued

                else:
                    # No -> evento en verde
                    tutorial_start = start.replace(hour=interval.hour, minute=interval.minute)
                    tutorial_end = tutorial_start + datetime.timedelta(minutes=30)
                    tutorials_json.append(
                        {'title': _('Available'), 'start': tutorial_start, 'end': tutorial_end,
                         'backgroundColor': 'green', 'className': 'tutorial-available'})

        start = start + datetime.timedelta(days=1)

    return JsonResponse(tutorials_json, safe=False)


def check_tutorials(day_tutorials, interval):
    for tutorial in day_tutorials:
        if tutorial.horainicio <= interval < tutorial.horafin:
            return tutorial
    return None


def check_match(interval, day_tutorials):
    for tutorial in day_tutorials:
        if tutorial.fechacita.time() == interval:
            return tutorial
    return None


def time_intervals(minutes):
    times = []
    for i in range(0, 24 * 4):
        datetime_to_add = (datetime.datetime.combine(datetime.date.today(), datetime.time()) + datetime.timedelta(
            minutes=minutes) * i).time()

        if datetime_to_add not in times:
            times.append(datetime_to_add)

    return times


def accept_from_mail(request):
    request_token = request.GET['token']
    tutorial_request_id = request.GET['id']
    tutorial_request = Peticioncita.objects.get(idcita=tutorial_request_id)

    assert PeticionCitaService.is_token_valid(tutorial_request, request_token)

    if PeticionCitaService.can_accept(tutorial_request):
        PeticionCitaService.accept(tutorial_request)
        messages.success(request, _('Tutorial request was accepted successfully.'))
    else:
        messages.error(request, _('You cannot accept this tutorial request due to a schedule incompatibility.'))

    return HttpResponseRedirect('/')
