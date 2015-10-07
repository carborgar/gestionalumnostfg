from principal.models import Titulacion
from django.db.models import Q
from django.shortcuts import get_object_or_404


def create_and_save(form):
    certification = Titulacion(
        codigo=form.cleaned_data['code'],
        nombre=form.cleaned_data['name']
    )
    certification.save()
    return certification


def find_all():
    return Titulacion.objects.all().order_by('nombre')


def find_by_code(code):
    try:
        certification = Titulacion.objects.get(codigo=code)
    except Titulacion.DoesNotExist:
        certification = None
    return certification


def find_by_subject(subject_id):
    return Titulacion.objects.filter(asignaturas=subject_id)


def search(search_text):
    return Titulacion.objects.filter(
        Q(nombre__icontains=search_text) |
        Q(codigo__icontains=search_text)).order_by('nombre')


def find_one(certification_id):
    return get_object_or_404(Titulacion, id=certification_id)
