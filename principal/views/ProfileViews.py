__author__ = 'Carlos'

from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from principal.forms import StudentProfileForm, AddressForm
from principal.models import Alumno, Profesor
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.forms.formsets import formset_factory
from principal.services import ProfileService
from django.contrib import messages
from django.utils.translation import ugettext as _
from principal.services import SubjectService
from principal.forms import RemarkForm, LecturerStudentFilterForm
from principal.services import RemarkService
from django.http import HttpResponseRedirect
from principal.forms import LecturerProfileForm


@login_required()
def view_profile(request, student_id):
    template_vars = {}
    form = None

    if request.method == 'POST':
        student = Alumno.objects.get(id=student_id)
        lecturer_subjects = SubjectService.get_lecturer_subjects(request.user.id)
        template_vars['lecturer_subjects'] = lecturer_subjects

        # Save remark from form -> logged user is a lecturer
        form = RemarkForm(request.POST, lecturer_id=request.user.id)
        if form.is_valid():
            RemarkService.save(form)
            messages.success(request, _('Remark was saved successfully.'))

            return HttpResponseRedirect('/profile/view/%s' % form.cleaned_data['student_id'])
    else:
        if request.user.has_perm('principal.alumno'):
            student = Alumno.objects.get(id=request.user.id)

        else:
            student = Alumno.objects.get(id=student_id)

            if request.user.has_perm('principal.profesor'):
                lecturer_subjects = SubjectService.get_lecturer_subjects(request.user.id)
                form = RemarkForm(lecturer_id=request.user.id, initial={'student_id': student.id})
                template_vars['lecturer_subjects'] = lecturer_subjects

    template_vars['student'] = student
    template_vars['form'] = form

    return render_to_response('profile/details.html', template_vars, context_instance=RequestContext(request))


@permission_required('principal.alumno')
def edit_profile(request):
    address_formset = formset_factory(AddressForm, max_num=2, extra=2)
    student = Alumno.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, student_id=student.id)
        formset = address_formset(request.POST)
        if form.is_valid() and formset.is_valid():
            ProfileService.reconstruct_and_save(form, formset, request.user.id)
            messages.success(request, _('Information has been saved successfully.'))
        elif len(request.FILES) > 0:
            # Warn the user to select the image again
            messages.warning(request, _('Please, select the profile photo again.'))

    else:

        form = StudentProfileForm(initial=ProfileService.get_form_data(student), student_id=student.id)
        formset = address_formset(initial=ProfileService.get_formset_data(student))

    return render_to_response('profile/edit.html', {'form': form, 'formset': formset, 'student': student},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def lecturer_students(request):
    if request.method == 'POST':
        form = LecturerStudentFilterForm(request.POST, lecturer_id=request.user.id)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            students = SubjectService.subject_students(subject, request.user.id)
    else:
        form = LecturerStudentFilterForm(lecturer_id=request.user.id)
        students = SubjectService.lecturer_students(request.user.id)

    return render_to_response('student/list.html', {'students': students, 'form': form},
                              context_instance=RequestContext(request))


@permission_required('principal.profesor')
def edit_lecturer(request):
    lecturer = Profesor.objects.get(id=request.user.id)

    if request.method == 'POST':
        form = LecturerProfileForm(request.POST)
        if form.is_valid():
            ProfileService.update_profile(lecturer, form)
            messages.success(request, _('Information was updated successfully'))
    else:
        initial_data = ProfileService.build_initial_profile_data(lecturer)
        form = LecturerProfileForm(initial=initial_data)

    return render_to_response('lecturer/edit.html', {'form': form}, context_instance=RequestContext(request))
