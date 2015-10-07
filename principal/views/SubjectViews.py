import csv
from django.contrib.messages.context_processors import messages

__author__ = 'Carlos'

import json as json_lib
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required, login_required
from django.http.response import JsonResponse, HttpResponseRedirect
from principal.services import SubjectService
from principal.forms import SubjectEditForm, FileUploadSubjectForm
from django.utils.translation import ugettext as _
from django.contrib import messages
from principal.models import Asignatura
from django.shortcuts import get_object_or_404
import xmltodict
import types


@login_required()
def list_subjects(request):
    if request.user.has_perm('principal.alumno'):
        subjects = SubjectService.get_student_subjects(request.user.alumno.id)
    elif request.user.has_perm('principal.profesor'):
        # TODO Creo que no llama al metodo correcto (Revisar Carlos)
        subjects = SubjectService.get_lecturer_subjects(request.user.profesor.id)
    else:
        # It's an administrator
        subjects = SubjectService.find_all().order_by('nombre')

    template_name = 'subject/list.html'
    template_data = {"subjects": subjects}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@login_required()
def search(request):
    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''

    if request.user.has_perm('principal.alumno'):
        subjects = SubjectService.get_student_subjects_search(request.user.alumno.id, search_text)
    elif request.user.has_perm('principal.profesor'):
        # TODO Creo que no llama al metodo correcto (Revisar Carlos)
        subjects = SubjectService.get_lecturer_subjects_search(request.user.profesor.id, search_text)
    else:
        # It's an administrator
        subjects = SubjectService.search(search_text)

    template_name = 'subject/ajax_search.html'
    template_data = {'subjects': subjects}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.alumno')
def get_all_json(request):
    subjects = SubjectService.get_student_subjects(request.user.alumno.id)
    json = json_lib.dumps([{'id': subject.id, 'name': subject.nombre} for subject in subjects])
    return JsonResponse(json, safe=False)


@permission_required('principal.administrator')
def create_subject(request):
    if request.POST:
        form = SubjectEditForm(request.POST)

        if form.is_valid():
            subject = SubjectService.create(form)
            SubjectService.save(subject)
            messages.success(request, _("Action completed successfully"))
            return HttpResponseRedirect("/admin/subject/link/" + str(subject.id))
    else:
        data = {}
        form = SubjectEditForm(initial=data)

    template_name = 'subject/edit.html'
    template_data = {"form": form}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def delete_subject(request, subject_id):
    subject = SubjectService.find_one(subject_id)
    title = subject.nombre
    subject.delete()
    messages.success(request, _('The subject ' + title + ' has been removed'))
    return HttpResponseRedirect('/subject/list')


@permission_required('principal.administrator')
def delete_users_subject(request, subject_id):
    subject = SubjectService.find_one(subject_id)
    students = subject.alumno_set.all()

    # Delete students
    for student in students:
        student.asignaturas.remove(subject)

    # Delete relationship with lecturers
    subject.imparteasignatura_set.all().delete()

    messages.success(request, _('The users have been removed'))
    return HttpResponseRedirect('/subject/details/' + str(subject_id))


@permission_required('principal.view_subject_details')
def subject_details(request, subject_id):
    subject = get_object_or_404(Asignatura, id=subject_id)
    certifications = subject.titulacion_set.all()
    subjects = subject.imparteasignatura_set.all()
    news = subject.noticia_set.all()
    template_name = 'subject/details.html'
    template_data = {'subject': subject, 'certifications': certifications, 'subject_lecturers': subjects, 'news': news}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def import_subject(request):
    template_data = {}
    import_errors_create = []
    import_errors_link = []
    subject_create = []
    subject_link = []

    if request.POST:

        form = FileUploadSubjectForm(request.POST, request.FILES)

        if form.is_valid():

            file_name = form.cleaned_data['file_upload']
            certifications = set(form.cleaned_data['certifications'])
            data = file_name.read()
            file_name.close()

            try:
                if form.cleaned_data['file_upload'].content_type == "text/xml":
                    # File XML
                    data = xmltodict.parse(data)

                    if data['asignaturas']:
                        if not isinstance(data['asignaturas']['asignatura'], list):
                            # 1 value
                            subject = data['asignaturas']['asignatura']
                            data_form = SubjectService.get_form_data_xml(subject)
                            create_link_subject_file(data_form, certifications, import_errors_create,
                                                     import_errors_link, subject_create, subject_link)
                        else:
                            for subject_data in data['asignaturas']['asignatura']:
                                data_form = SubjectService.get_form_data_xml(subject_data)
                                create_link_subject_file(data_form, certifications, import_errors_create,
                                                         import_errors_link, subject_create, subject_link)
                else:

                    # File CSV
                    for subject in csv.reader(data.splitlines()):
                        data_form = SubjectService.get_form_data_csv(subject)
                        create_link_subject_file(data_form, certifications, import_errors_create, import_errors_link,
                                                 subject_create, subject_link)

                if not import_errors_create and not import_errors_link:
                    message = _('Action completed successfully')
                    messages.success(request, message)
                else:
                    if import_errors_create:
                        template_data['import_errors_create'] = import_errors_create
                    if import_errors_link:
                        template_data['import_errors_link'] = import_errors_link
                    if import_errors_create or import_errors_link:
                        message = _('Action completed successfully')
                        messages.warning(request, message)

                form = FileUploadSubjectForm()

            except KeyError as e:
                message = _("The file structure is wrong. It needs a label called: " + e.message)
                form.add_error('file_upload', message)
                SubjectService.rollback(subject_create, subject_link, certifications)
            except AttributeError:
                message = _("Please, check the attributes of the subjects")
                form.add_error('file_upload', message)
                SubjectService.rollback(subject_create, subject_link, certifications)
            except TypeError:
                message = _("Please, check the xml syntax and data values")
                form.add_error('file_upload', message)
                SubjectService.rollback(subject_create, subject_link, certifications)
            except Exception:
                message = _("Please, check the file")
                form.add_error('file_upload', message)
                SubjectService.rollback(subject_create, subject_link, certifications)

    else:
        form = FileUploadSubjectForm()

    template_data['form'] = form
    template_name = 'subject/import_subject.html'
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


def create_link_subject_file(data_form, certifications, import_errors_create, import_errors_link, subject_create,
                             subject_link):
    form_subject = SubjectEditForm(data=data_form)

    if form_subject.is_valid():
        subject = SubjectService.create(form_subject)
        SubjectService.save(subject)
        subject_create.append(subject)
        [subject.titulacion_set.add(certification) for certification in list(certifications)]
    else:
        import_errors_create.append(form_subject.data['name'] + " - " + form_subject.data['code'])
        subject = SubjectService.find_by_code(form_subject.data['code'])
        if subject:
            [subject.titulacion_set.add(certification) for certification in list(certifications)]
            subject_link.append(subject)
        else:
            import_errors_link.append(form_subject.data['name'] + " - " + form_subject.data['code'])
