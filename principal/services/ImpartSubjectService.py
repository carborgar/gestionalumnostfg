from principal.models import Imparteasignatura
from principal.services import LecturerService, SubjectService, UserService


def reconstruct_and_save(form):

    lecturer_id = form.cleaned_data['lecturer_id']
    subject_id = form.cleaned_data['subject_id']

    lecturer = LecturerService.find_one(lecturer_id)
    subject = SubjectService.find_one(subject_id)
    position = form.cleaned_data['position']

    impart_subject = Imparteasignatura.objects.create(
        cargo=position,
        asignatura=subject,
        profesor=lecturer
    )

    return impart_subject


def get_form_data_xml(lecturer, subject):
    data = {}
    if lecturer:

        subject_id = subject.id
        data['subject_id'] = subject_id

        user = UserService.find_by_username(lecturer['uvus'])
        if user is not None:
            data['lecturer_id'] = user.id
            data['lecturer'] = user.first_name + user.last_name

        position = lecturer['cargo']
        data['position'] = position

    return data


def get_form_data_csv(lecturer, subject):

    data = {}
    if lecturer:

        subject_id = subject.id
        data['subject_id'] = subject_id

        user = UserService.find_by_username(lecturer[3])
        if user is not None:
            data['lecturer_id'] = user.id
            data['lecturer'] = user.first_name + " " + user.last_name

        position = lecturer[5]
        data['position'] = position

    return data
