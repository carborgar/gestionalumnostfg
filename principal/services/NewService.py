__author__ = 'Carlos'

from principal.models import Noticia, Profesor
from django.shortcuts import get_object_or_404


def build_initial(new_id):
    if new_id:
        new = get_object_or_404(Noticia, id=new_id)
        return {'title': new.titulo, 'body': new.texto, 'new_id': new_id, 'subject': new.asignatura}
    else:
        return {}


def save(form, lecturer_id):
    new_id = form.cleaned_data['new_id']
    subject = form.cleaned_data['subject']
    title = form.cleaned_data['title']
    body = form.cleaned_data['body']
    lecturer = Profesor.objects.get(id=lecturer_id)

    if not new_id:
        Noticia.objects.create(titulo=title, texto=body, asignatura=subject, profesor=lecturer)
    else:
        new = Noticia.objects.get(id=new_id)
        new.titulo = title
        new.texto = body
        new.asignatura = subject

        new.save()


def delete(new_id):
    Noticia.objects.get(id=new_id).delete()

