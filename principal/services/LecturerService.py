# -*- coding: utf-8 -*-

from django.db.models import Q
from django.shortcuts import get_object_or_404
from principal.models import Imparteasignatura
from principal.models import Profesor
from django.contrib.auth.models import Permission
from principal.utils.GestionAlumnosUtils import id_generator


def lecturers_of_subject(subject_id):
    return [ia.profesor for ia in Imparteasignatura.objects.filter(asignatura_id=subject_id)]


def student_lecturers(student):
    result = []

    for subject in student.asignaturas.all():
        result += lecturers_of_subject(subject.id)

    return result


def create(form):
    lecturer = Profesor(
        username=form.cleaned_data['user'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        dni=form.cleaned_data['dni'],
        is_active=True,
    )

    if form.cleaned_data['email']:
        lecturer.email = form.cleaned_data['email']
    else:
        lecturer.email = form.cleaned_data['user'] + '@us.es'

    # Encrypt password
    password = id_generator()
    lecturer.set_password(password)

    return lecturer


def save(lecturer):
    lecturer.save()  # A DB object is needed

    lecturer.user_permissions.add(Permission.objects.get(codename="profesor"))
    lecturer.user_permissions.add(Permission.objects.get(codename="view_certification_list"))
    lecturer.user_permissions.add(Permission.objects.get(codename="view_tutorial_request_list"))

    lecturer.save()  # Save again with permissions


def find_one(user_id):
    return get_object_or_404(Profesor, id=user_id)


def fin_all():
    return Profesor.objects.all()


def search(search_text):
    return Profesor.objects.filter(Q(username__icontains=search_text) | Q(first_name__icontains=search_text) | Q(
        last_name__icontains=search_text)).order_by('last_name')


def get_form_data_xml(lecturer):
    data = {}
    if lecturer:
        data = {
            'user': lecturer['uvus'],
            'first_name': lecturer['nombre'],
            'last_name': lecturer['apellidos'],
            'dni': lecturer['dni'],
            'type': 'le',
        }

        try:
            data['email'] = lecturer['correo']
        except KeyError:
            pass

    return data


def get_form_data_csv(lecturer):
    data = {}
    if lecturer:
        fullname = lecturer[2].split(',', 2)
        data = {
            'dni': lecturer[1],
            'user': lecturer[3],
            'first_name': fullname[1],
            'last_name': fullname[0],
            'type': 'le'
        }
        if lecturer[4] != 'null':
            data['email'] = lecturer[4]

    return data


def find_by_dni(dni):
    try:
        lecturer = Profesor.objects.get(dni=dni)
    except Profesor.DoesNotExist:
        lecturer = None
    return lecturer
