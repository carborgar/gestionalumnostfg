__author__ = 'Carlos'

from principal.models import Alumno, Profesor, Peticioncita
from datetime import timedelta
import hashlib
from principal.views import EmailViews


def create(form, student_id):
    lecturer = Profesor.objects.get(id=form.cleaned_data['lecturer'])
    return Peticioncita(
        alumno=Alumno.objects.get(id=student_id),
        profesor=lecturer,
        fechacita=form.cleaned_data['date'],
        fechacitafin=form.cleaned_data['date'] + timedelta(minutes=30),
        motivo=form.cleaned_data['motivation'],
        estado='EC'
    )


# Returns the tutorial request to automatically cancel (Busy schedule)
# That means: 'EN CURSO' requests for the same lecturer and datetime excluding the request to accept
def request_by_hour(lecturer, request_to_compare):
    return Peticioncita.objects.exclude(idcita=request_to_compare.idcita).filter(profesor=lecturer,
                                                                                 fechacita=request_to_compare.fechacita,
                                                                                 estado='EC')


# Returns true when there is no accepted request on the same date
def can_accept(request_to_accept):
    return Peticioncita.objects.filter(profesor=request_to_accept.profesor, fechacita=request_to_accept.fechacita,
                                       estado='AC').count() == 0


# Accepts the given request and automatically cancels the requests with the same datetime.
def accept(request_to_accept):
    cancel_concurrent_requests(request_to_accept)
    request_to_accept.estado = 'AC'
    request_to_accept.save()


def cancel_concurrent_requests(request):
    same_hour_requests = request_by_hour(request.profesor, request)
    for tutorial_request in same_hour_requests:
        auto_cancel(tutorial_request)


def auto_cancel(request_to_cancel):
    request_to_cancel.estado = 'CA'
    request_to_cancel.motivocancelacion = 'There is another accepted request for this date.'

    request_to_cancel.save()

    EmailViews.send_tutorial_rejected_mail(request_to_cancel)


def cancel(deny_form):
    tutorial_request = Peticioncita.objects.get(idcita=deny_form.cleaned_data['request_id'])
    tutorial_request.motivocancelacion = deny_form.cleaned_data['motivation']
    tutorial_request.estado = 'DE'
    tutorial_request.save()

    EmailViews.send_tutorial_rejected_mail(tutorial_request)


def lecturer_requests(lecturer_id, state):
    return Peticioncita.objects.filter(profesor__id=lecturer_id, estado=state).order_by('-fechacita')


def student_requests(student_id, state=None):
    if state:
        return Peticioncita.objects.filter(alumno__id=student_id, estado=state).order_by('-fechacita')
    else:
        return Alumno.objects.get(id=student_id).peticioncita_set.all()


def cancel_all(tutorial_request_list, motivation):
    for t in tutorial_request_list:
        t.motivocancelacion = motivation
        t.estado = 'DE'
        t.save()

        EmailViews.send_tutorial_rejected_mail(t)


def can_request(tutorial_request):
    # Business rule: a student cannot request more than two appointments for the same lecturer and day.
    appointment_date = tutorial_request.fechacita.date()
    appointment_day = appointment_date.day
    appointment_month = appointment_date.month
    appointment_year = appointment_date.year

    parameters = [appointment_year, appointment_month, appointment_day, tutorial_request.profesor.id,
                  tutorial_request.alumno.id]

    query = '''SELECT idCita FROM peticioncita
                      WHERE YEAR(fechaCita)=%s AND MONTH(fechaCita)=%s
                      AND DAY(fechaCita)=%s AND profesor=%s AND alumno=%s'''

    same_day_same_lecturer = len(list(Peticioncita.objects.raw(query, parameters)))

    return same_day_same_lecturer < 2


def auto_assign(auto_assign_tutorial_form, lecturer):
    return Peticioncita.objects.create(
        alumno=auto_assign_tutorial_form.cleaned_data['student'],
        profesor=lecturer,
        fechacita=auto_assign_tutorial_form.cleaned_data['date'],
        fechacitafin=auto_assign_tutorial_form.cleaned_data['date'] + timedelta(minutes=30),
        motivo=auto_assign_tutorial_form.cleaned_data['motivation'],
        estado='AC'
    )


def is_token_valid(tutorial_request, token):
    return token == hashlib.sha512(str(tutorial_request.activation_hash).encode('utf-8')).hexdigest()