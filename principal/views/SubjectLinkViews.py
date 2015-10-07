import csv
import types
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import xmltodict
from principal.services import SubjectService, CertificationService, UserService, StudentService, LecturerService, \
    ImpartSubjectService, EmailService
from principal.forms import SubjectLinkEditForm, UserLinkSubjectForm, FileUploadSubjectLinkForm, UserEditForm
from django.utils.translation import ugettext as _
from django.contrib import messages
from principal.models import Asignatura, Alumno, Profesor
from principal.utils.GestionAlumnosUtils import id_generator


@permission_required('principal.administrator')
def create(request, subject_id):
    subject = SubjectService.find_one(subject_id)
    assert subject is not None

    if request.POST:
        form = SubjectLinkEditForm(request.POST)
        if form.is_valid():
            subject = SubjectService.edit(form)
            SubjectService.save(subject)
            messages.success(request, _("Action completed successfully"))
            return HttpResponseRedirect("/subject/details/" + str(subject_id))
    else:
        certifications = CertificationService.find_by_subject(subject_id)
        data = {'id': subject_id, 'certifications': certifications}
        form = SubjectLinkEditForm(initial=data)

    template_name = 'subject_link/edit.html'
    template_data = {"form": form, "id": subject_id}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def link_user_subject(request, subject_id, user_id):
    subject = SubjectService.find_one(subject_id)
    assert subject is not None

    if user_id is None:
        students = StudentService.find_all()
        lecturers = LecturerService.fin_all()
        template_name = 'user/list.html'
        template_data = {'students': students, 'lecturers': lecturers, 'subject_id': subject.id}
        return render_to_response(template_name, template_data, context_instance=RequestContext(request))
    else:
        user = UserService.find_one(user_id)
        assert user.has_perm('principal.alumno') or user.has_perm('principal.profesor')

        if user.has_perm('principal.alumno'):
            student = StudentService.find_one(user.id)
            student.asignaturas.add(subject)
        else:
            lecturer = LecturerService.find_one(user.id)

            if request.POST:
                form = UserLinkSubjectForm(request.POST)
                if form.is_valid():
                    ImpartSubjectService.reconstruct_and_save(form)
                    messages.success(request, _("Action completed successfully"))
                    return HttpResponseRedirect('/subject/details/' + str(subject_id))
            else:
                data = {'subject_id': subject_id, 'lecturer_id': lecturer.id,
                        'lecturer': lecturer.first_name + " " + lecturer.last_name}
                form = UserLinkSubjectForm(initial=data)

            students = StudentService.find_all()
            lecturers = LecturerService.fin_all()

            template_name = 'user/list.html'
            template_data = {"form": form, 'students': students, 'lecturers': lecturers, 'subject_id': subject_id,
                             'lecturer_id': lecturer.id}
            return render_to_response(template_name, template_data, context_instance=RequestContext(request))

        messages.success(request, _('User linked to the subject'))
        return HttpResponseRedirect('/subject/details/' + str(subject_id))


@permission_required('principal.administrator')
def unlink_user_subject(request, subject_id, user_id):
    subject = SubjectService.find_one(subject_id)
    user = UserService.find_one(user_id)
    assert not user.has_perm('principal.administrator')

    if user.has_perm('principal.alumno'):
        student = StudentService.find_one(user_id)
        student.asignaturas.remove(subject)
    else:
        lecturer = LecturerService.find_one(user_id)
        lecturer.imparteasignatura_set.all().get(profesor_id=user.id, asignatura_id=subject.id).delete()

    messages.success(request, _('Subject unlinked to the user'))
    return HttpResponseRedirect('/admin/user/details/' + str(user.id))


@permission_required('principal.administrator')
def unlink_certification_subject(request, subject_id, certification_id):
    subject = SubjectService.find_one(subject_id)
    certification = CertificationService.find_one(certification_id)
    subject.titulacion_set.remove(certification)
    messages.success(request, _('Subject unlinked to the certification'))
    return HttpResponseRedirect('/admin/certification/details/' + str(certification_id))


@permission_required('principal.administrator')
def import_link_subject(request, subject_id):
    template_data = {}
    initial = {}
    import_errors_link = []
    user_create = {}
    student_link = []
    lecturer_link = []

    subject = get_object_or_404(Asignatura, id=subject_id)
    initial['subject'] = subject.id
    initial['subject_name'] = subject.nombre

    if request.POST:

        form = FileUploadSubjectLinkForm(request.POST, request.FILES)

        if form.is_valid():

            file_name = form.cleaned_data['file_upload']
            subject = get_object_or_404(Asignatura, id=form.cleaned_data['subject'])
            data = file_name.read()
            file_name.close()
            file_type = form.cleaned_data['file_upload'].content_type

            try:
                if file_type == "text/xml":

                    # File XML
                    data = xmltodict.parse(data)

                    # Import students
                    if data['usuarios']['alumnos']:
                        if not isinstance(data['usuarios']['alumnos']['alumno'], list):
                            # 1 value
                            student_data = data['usuarios']['alumnos']['alumno']
                            create_link_student_file(student_data, subject, file_type,
                                                     import_errors_link, user_create, student_link)
                        else:
                            for student_data in data['usuarios']['alumnos']['alumno']:
                                create_link_student_file(student_data, subject, file_type,
                                                         import_errors_link, user_create, student_link)

                    # Import lecturers
                    if data['usuarios']['profesores']:
                        if not isinstance(data['usuarios']['profesores']['profesor'], list):
                            # 1 value
                            lecturer_data = data['usuarios']['profesores']['profesor']
                            create_link_lecturer_file(lecturer_data, subject, file_type,
                                                      import_errors_link, user_create, lecturer_link)
                        else:
                            for lecturer_data in data['usuarios']['profesores']['profesor']:
                                create_link_lecturer_file(lecturer_data, subject, file_type,
                                                          import_errors_link, user_create, lecturer_link)
                else:
                    # File CSV
                    for user in csv.reader(data.splitlines()):
                        type_user = user[0]
                        if type_user == 'Alumno':
                            create_link_student_file(user, subject, file_type, import_errors_link,
                                                     user_create, lecturer_link)
                        elif type_user == 'Profesor':
                            create_link_lecturer_file(user, subject, file_type,
                                                      import_errors_link, user_create, lecturer_link)
                        else:
                            raise KeyError('Alumno o Profesor')

                if import_errors_link:
                    message = _('Action completed successfully')
                    messages.warning(request, message)
                    template_data['import_errors_link'] = import_errors_link
                else:
                    EmailService.send_email_create_user(user_create, request)
                    messages.success(request, _('Action completed successfully'))
                    return HttpResponseRedirect("/subject/details/" + str(subject.id))

                form = FileUploadSubjectLinkForm(initial=initial)

            except KeyError as e:
                message = _("The file structure is wrong. It needs a label called:: " + e.message)
                form.add_error('file_upload', message)
                UserService.rollback(user_create, student_link, lecturer_link, subject_id)
            except AttributeError:
                message = _("Please, check the attributes of the users")
                form.add_error('file_upload', message)
                UserService.rollback(user_create, student_link, lecturer_link, subject_id)
            except TypeError:
                message = _("Please, check the xml syntax and data values")
                form.add_error('file_upload', message)
                UserService.rollback(user_create, student_link, lecturer_link, subject_id)
            except Exception:
                message = _("Please, check the file")
                form.add_error('file_upload', message)
                UserService.rollback(user_create, student_link, lecturer_link, subject_id)

    else:
        form = FileUploadSubjectLinkForm(initial=initial)

    template_data['subject'] = subject
    template_data['form'] = form
    template_name = 'subject_link/import_subject_link.html'
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


def create_link_student_file(student_data, subject, file_type, import_errors_link, user_create,
                             user_link):
    if file_type == "text/xml":
        data_form = StudentService.get_form_data_xml(student_data)
    else:
        data_form = StudentService.get_form_data_csv(student_data)

    form_student = UserEditForm(data=data_form)

    if form_student.is_valid():
        student = StudentService.create(form_student)
        StudentService.save(student)
        password = id_generator()
        UserService.save_password(student, password)
        user_create[student] = password
        student.asignaturas.add(subject)
    else:
        fullname = form_student.data['last_name'] + ", " + form_student.data['first_name']
        username = form_student.data['user']
        user = UserService.find_by_username(username)
        if user:
            student = Alumno.objects.get(id=user.id)
            if student:
                student.asignaturas.add(subject)
                user_link.append(student)
            else:
                import_errors_link.append(_("Student") + ": " + fullname + " - " + form_student.data['dni'])
        else:
            import_errors_link.append(_("Student") + ": " + fullname + " - " + form_student.data['dni'])


def create_link_lecturer_file(lecturer_data, subject, file_type, import_errors_link, user_create,
                              user_link):
    if file_type == "text/xml":
        data_form = LecturerService.get_form_data_xml(lecturer_data)
    else:
        data_form = LecturerService.get_form_data_csv(lecturer_data)

    form_lecturer = UserEditForm(data=data_form)

    if form_lecturer.is_valid():
        lecturer = LecturerService.create(form_lecturer)
        LecturerService.save(lecturer)
        password = id_generator()
        UserService.save_password(lecturer, password)
        user_create[lecturer] = password

        if file_type == "text/xml":
            data_form_link = ImpartSubjectService.get_form_data_xml(lecturer_data, subject)
        else:
            data_form_link = ImpartSubjectService.get_form_data_csv(lecturer_data, subject)

        form_lecturer_link = UserLinkSubjectForm(data=data_form_link)

        if form_lecturer_link.is_valid():
            ImpartSubjectService.reconstruct_and_save(form_lecturer_link)
        else:
            fullname = form_lecturer.data['last_name'] + ", " + form_lecturer.data['first_name']
            import_errors_link.append(_("Lecturer") + ": " + fullname + " - " + form_lecturer.data['dni'])

    else:

        if file_type == "text/xml":
            data_form_link = ImpartSubjectService.get_form_data_xml(lecturer_data, subject)
        else:
            data_form_link = ImpartSubjectService.get_form_data_csv(lecturer_data, subject)

        form_lecturer_link = UserLinkSubjectForm(data=data_form_link)

        if form_lecturer_link.is_valid():
            lecturer_id = form_lecturer_link.data['lecturer_id']
            lecturer = Profesor.objects.get(id=lecturer_id)
            fullname = form_lecturer.data['last_name'] + ", " + form_lecturer.data['first_name']

            if lecturer:
                if form_lecturer_link.is_valid():
                    ImpartSubjectService.reconstruct_and_save(form_lecturer_link)
                    user_link.append(lecturer)
                else:
                    import_errors_link.append(_("Lecturer") + ": " + fullname + " - " + form_lecturer.data['dni'])
            else:
                import_errors_link.append(_("Lecturer") + ": " + fullname + " - " + form_lecturer.data['dni'])
        else:
            fullname = form_lecturer.data['last_name'] + ", " + form_lecturer.data['first_name']
            import_errors_link.append(_("Lecturer") + ": " + fullname + " - " + form_lecturer.data['dni'])
