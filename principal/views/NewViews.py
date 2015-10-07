__author__ = 'Carlos'

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from principal.forms import NewForm
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from principal.services import SubjectService, NewService
from principal.models import Noticia, Asignatura
from django.shortcuts import get_object_or_404


@login_required()
def news(request, new_id=None, method=None):
    if request.method == 'POST':
        assert request.user.has_perm('principal.profesor')
        form = NewForm(request.POST, lecturer_id=request.user.id)

        if form.is_valid():
            NewService.save(form, request.user.id)
            messages.add_message(request, messages.SUCCESS, _('Action completed successfully.'))

            return HttpResponseRedirect('/news')

    if request.user.has_perm('principal.alumno'):
        subjects = SubjectService.get_student_subjects(request.user.id)
        form = None

    elif request.user.has_perm('principal.profesor'):
        subjects = SubjectService.get_lecturer_subjects(request.user.id)
        if method == 'rm':
            new = get_object_or_404(Noticia, id=new_id)
            if new.profesor.id == request.user.id:
                NewService.delete(new_id)
                messages.success(request, _('New was deleted successfully.'))
            else:
                messages.error(request, _('You cannot delete this new.'))
            return HttpResponseRedirect('/news')

        elif method == 'ed':
            new = get_object_or_404(Noticia, id=new_id)
            if new.profesor.id == request.user.id:
                initial_data = NewService.build_initial(new_id)
                form = NewForm(lecturer_id=request.user.id, initial=initial_data)
            else:
                messages.error(request, _('You cannot edit this new.'))
                return HttpResponseRedirect('/news')
        elif not method:
            form = NewForm(lecturer_id=request.user.id)

    else:
        subjects = Asignatura.objects.all()
        form = None

    return render_to_response('new/list.html', {'subjects': subjects, 'form': form},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def edit_new(request, new_id):
    form = None
    if request.method == 'POST':
        form = NewForm(request.POST)
        if form.is_valid():
            pass
            # save
    else:
        initial_data = NewService.build_initial(new_id)
        form = NewForm(initial=initial_data)

    return render_to_response('new/edit.html', {'form', ls}, context_instance=RequestContext(request))