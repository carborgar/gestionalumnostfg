# -*- coding: utf-8 -*-


from django.db.models import Q
from django.shortcuts import get_object_or_404
from principal.models import Alumno
from django.contrib.auth.models import Permission
from principal.utils.GestionAlumnosUtils import id_generator


def create(form):
    student = Alumno(
        username=form.cleaned_data['user'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        dni=form.cleaned_data['dni'],
        is_active=True,
    )

    if form.cleaned_data['email']:
        student.email = form.cleaned_data['email']
    else:
        student.email = form.cleaned_data['user'] + '@alum.us.es'

    # Encrypt password
    password = id_generator()
    student.set_password(password)

    return student


def save(student):
    student.save()  # A DB object is needed

    student.user_permissions.add(Permission.objects.get(codename='alumno'))
    student.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
    student.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
    student.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

    student.save()  # Save again with permissions


def find_one(user_id):
    return get_object_or_404(Alumno, id=user_id)


def find_all():
    return Alumno.objects.all()


def search(search_text):
    return Alumno.objects.filter(Q(username__icontains=search_text) | Q(first_name__icontains=search_text) | Q(
        last_name__icontains=search_text)).order_by('last_name')


def get_form_data_xml(student):
    data = {}
    if student:
        data = {
            'user': student['uvus'],
            'first_name': student['nombre'],
            'last_name': student['apellidos'],
            'dni': student['dni'],
            'type': 'st'
        }

        try:
            data['email'] = student['correo']
        except KeyError:
            pass

    return data


def get_form_data_csv(student):
    data = {}
    if student:
        fullname = student[2].split(',', 2)
        data = {
            'user': student[3],
            'dni': student[1],
            'first_name': fullname[1],
            'last_name': fullname[0],
            'type': 'st'
        }
        try:
            data['email'] = student[4]
        except IndexError:
            pass
    return data


def find_by_dni(dni):
    try:
        student = Alumno.objects.get(dni=dni)
    except Alumno.DoesNotExist:
        student = None
    return student
