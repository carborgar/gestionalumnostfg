# -*- coding: utf-8 -*-


from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from principal.forms import UserEditForm, FileUploadForm
from django.http.response import HttpResponseRedirect
from django.utils.translation import ugettext as _
from principal.services import LecturerService, StudentService, UserService, EmailService
from django.contrib import messages
import types
import xmltodict
import csv
from principal.utils.GestionAlumnosUtils import id_generator


@permission_required('principal.administrator')
def create_user(request):
    if request.POST:
        form = UserEditForm(request.POST)
        if form.is_valid():

            if form.cleaned_data['type'] == 'st':
                # Is student
                user = StudentService.create(form)
                StudentService.save(user)
            elif form.cleaned_data['type'] == 'le':
                # Is lecturer
                user = LecturerService.create(form)
                LecturerService.save(user)
            password = id_generator()
            UserService.save_password(user, password)
            user_create = {user: password}
            EmailService.send_email_create_user(user_create, request)
            messages.success(request, _("Action completed successfully"))
            return HttpResponseRedirect("/admin/user/create")
    else:
        data = {}
        form = UserEditForm(initial=data)

    template_name = 'user/edit.html'
    template_data = {"form": form}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def list_users(request):
    students = StudentService.find_all()
    lecturers = LecturerService.fin_all()
    template_name = 'user/list.html'
    template_data = {'students': students, 'lecturers': lecturers}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def search(request):
    template_data = {}
    if request.POST:
        search_text = request.POST['search_text']
        if request.POST.get('subject_id'):
            subject_id = request.POST['subject_id']
            template_data['subject_id'] = subject_id
    else:
        search_text = ''

    students = StudentService.search(search_text)
    lecturers = LecturerService.search(search_text)
    template_data['students'] = students
    template_data['lecturers'] = lecturers
    template_name = 'user/ajax_search.html'
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def delete_user(request, user_id):
    try:
        user = UserService.find_one(user_id)
        assert not user.has_perm('principal.administrator')
        username = user.username
        UserService.delete(user)
        messages.success(request, _('The user ' + username + ' has been removed'))
    except AssertionError:
        messages.error(request, _('Could not delete the user'))
    return HttpResponseRedirect('/admin/user/list')


@permission_required('principal.administrator')
def details_user(request, user_id):
    template_data = {}
    try:
        user = UserService.find_one(user_id)
        assert not user.has_perm('principal.administrator')

        if user.has_perm('principal.alumno'):
            # Is student
            student = StudentService.find_one(user.id)
            subjects = student.asignaturas.all()
            template_data['subjects'] = subjects
            template_data['rol'] = 'alumno'
            template_data['user_details'] = student
        else:
            # Is lecturer
            lecturer = LecturerService.find_one(user.id)
            impart_subject = lecturer.imparteasignatura_set.all()
            template_data['impart_subjects'] = impart_subject
            template_data['rol'] = 'profesor'
            template_data['user_details'] = lecturer

        template_name = 'user/details.html'
        return render_to_response(template_name, template_data, context_instance=RequestContext(request))

    except AssertionError:
        messages.error(request, _('Unable to display user details'))
        return HttpResponseRedirect('/admin/user/list')


@permission_required('principal.administrator')
def import_users(request):

    template_data = {}
    import_errors_create = []
    user_create = {}

    if request.POST:
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_name = form.cleaned_data['file_upload']
            data = file_name.read()
            file_name.close()

            try:
                if form.cleaned_data['file_upload'].content_type == "text/xml":
                    # File XML
                    data = xmltodict.parse(data)

                    # Iterate students
                    if data['usuarios']['alumnos']:
                        if not isinstance(data['usuarios']['alumnos']['alumno'], list):
                            # 1 value
                            student_data = data['usuarios']['alumnos']['alumno']
                            data_form = StudentService.get_form_data_xml(student_data)
                            create_student_file(data_form, import_errors_create, user_create)
                        else:
                            for student_data in data['usuarios']['alumnos']['alumno']:
                                data_form = StudentService.get_form_data_xml(student_data)
                                create_student_file(data_form, import_errors_create, user_create)

                    # Iterate lecturers
                    if data['usuarios']['profesores']:
                        if not isinstance(data['usuarios']['profesores']['profesor'], list):
                            # 1 value
                            lecturer_data = data['usuarios']['profesores']['profesor']
                            data_form = LecturerService.get_form_data_xml(lecturer_data)
                            create_lecturer_file(data_form, import_errors_create, user_create)
                        else:
                            for lecturer_data in data['usuarios']['profesores']['profesor']:
                                data_form = LecturerService.get_form_data_xml(lecturer_data)
                                create_lecturer_file(data_form, import_errors_create, user_create)

                else:
                    # File CSV
                    for user in csv.reader(data.splitlines()):
                        type_user = user[0]
                        if type_user == 'Alumno':
                            data_form = StudentService.get_form_data_csv(user)
                            create_student_file(data_form, import_errors_create, user_create)
                        elif type_user == 'Profesor':
                            data_form = LecturerService.get_form_data_csv(user)
                            create_lecturer_file(data_form, import_errors_create, user_create)
                        else:
                            raise KeyError('Alumno o Profesor')

                message = _('Action completed successfully')
                EmailService.send_email_create_user(user_create, request)
                if import_errors_create:
                    messages.warning(request, message)
                    template_data['import_errors_create'] = import_errors_create
                else:
                    messages.success(request, message)

                form = FileUploadForm()

            except KeyError as e:
                message = _("The file structure is wrong. It needs a label called: ") + e.message
                form.add_error('file_upload', message)
                UserService.rollback_users(user_create)
            except AttributeError:
                message = _("Please, check the attributes of the subjects")
                form.add_error('file_upload', message)
                UserService.rollback_users(user_create)
            except TypeError:
                message = _("Please, check the xml syntax and data values")
                form.add_error('file_upload', message)
                UserService.rollback_users(user_create)
            except Exception:
                message = _("Please, check the file")
                form.add_error('file_upload', message)
                UserService.rollback_users(user_create)

    else:
        form = FileUploadForm()

    template_data['form'] = form
    template_name = 'user/import_user.html'
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


def create_student_file(data_form, import_errors_create, user_create):

    form_student = UserEditForm(data=data_form)
    if form_student.is_valid():
        student = StudentService.create(form_student)
        StudentService.save(student)
        password = id_generator()
        UserService.save_password(student, password)
        user_create[student] = password
    else:
        fullname = form_student.data['last_name'] + ", " + form_student.data['first_name']
        import_errors_create.append(_("Student") + ": " + fullname + " - " + form_student.data['dni'])


def create_lecturer_file(data_form, import_errors_create, user_create):

    form_lecturer = UserEditForm(data=data_form)
    if form_lecturer.is_valid():
        lecturer = LecturerService.create(form_lecturer)
        LecturerService.save(lecturer)
        password = id_generator()
        UserService.save_password(lecturer, password)
        user_create[lecturer] = password
    else:
        fullname = form_lecturer.data['last_name'] + ", " + form_lecturer.data['first_name']
        import_errors_create.append(_("Lecturer") + ": " + fullname + " - " + form_lecturer.data['dni'])
