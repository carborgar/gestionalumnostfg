__author__ = 'Carlos'

from principal.models import Tutoria


def update(tutorial_form, lecturer):
    old_id = tutorial_form.cleaned_data['tutorial_id']
    if old_id:
        # Edit the current tutorial
        old_tutorial = Tutoria.objects.get(id=old_id)
        assert old_tutorial.profesor == lecturer
        old_tutorial.dia = tutorial_form.cleaned_data['day']
        old_tutorial.horainicio = tutorial_form.cleaned_data['start_hour']
        old_tutorial.horafin = tutorial_form.cleaned_data['finish_hour']
        old_tutorial.save()

    else:
        Tutoria.objects.create(
            horainicio=tutorial_form.cleaned_data['start_hour'],
            horafin=tutorial_form.cleaned_data['finish_hour'],
            dia=tutorial_form.cleaned_data['day'],
            profesor=lecturer
        )

def enable_tutorials(lecturer):
    lecturer.tutoriaactivada = True
    lecturer.save()

def disable_tutorials(lecturer, motivation):
    lecturer.tutoriaactivada = False
    lecturer.motivotutorias = motivation
    lecturer.save()
