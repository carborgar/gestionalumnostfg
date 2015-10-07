__author__ = 'Carlos'

from principal.models import Observacion, Profesor, Alumno


def save(remark_form):
    Observacion.objects.create(
        descripcion=remark_form.cleaned_data['text'],
        profesor=Profesor.objects.get(id=remark_form.cleaned_data['lecturer_id']),
        alumno=Alumno.objects.get(id=remark_form.cleaned_data['student_id']),
        asignatura=remark_form.cleaned_data['subject']
    )
