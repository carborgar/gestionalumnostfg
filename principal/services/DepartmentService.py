from django.shortcuts import get_object_or_404
from principal.models import Departamento
from django.db.models import Q


def reconstruct_and_save(form):

    department = Departamento()

    if form.cleaned_data['id']:
        department.id = form.cleaned_data['id']

    department.codigo = form.cleaned_data['code']
    department.nombre = form.cleaned_data['name']
    department.web = form.cleaned_data['web']
    department.save()
    return department


def find_all():

    return Departamento.objects.all().order_by('nombre')


def find_by_code(code):

    try:
        department = Departamento.objects.get(codigo=code)
    except Departamento.DoesNotExist:
        department = None
    return department


def find_one(department_id):

    return get_object_or_404(Departamento, id=department_id)


def get_form_data(department):

    data = {}
    if department:
        data = {
            'id': department.id,
            'code': department.codigo,
            'name': department.nombre,
            'web': department.web
        }

    return data


def search(search_text):

    return Departamento.objects.filter(
        Q(nombre__icontains=search_text) |
        Q(codigo__icontains=search_text) |
        Q(web__icontains=search_text)).order_by('nombre')


def get_form_data_xml(department):

    data = {}
    if department:
        data = {
            'code': department['codigo'],
            'name': department['nombre'],
            'web': department['web']
        }

    return data


def rollback(department_create):

    for department in department_create:
        department.delete()


def get_form_data_csv(department):

    data = {}
    if department:
        data = {
            'code': department[0],
            'name': department[1],
            'web': department[2]
        }

    return data
