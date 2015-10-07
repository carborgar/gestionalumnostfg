from principal.models import Alumno, Imparteasignatura, Asignatura
from principal.services import DepartmentService
from django.db.models import Q


def get_student_subjects(student_id):
    student = Alumno.objects.get(id=student_id)
    return student.asignaturas.all().order_by('nombre')


def get_lecturer_subjects(lecturer_id):
    return Asignatura.objects.filter(
        id__in=[a.asignatura.id for a in Imparteasignatura.objects.filter(profesor_id=lecturer_id)]).order_by('nombre')


def create(form):
    subject = Asignatura()
    subject.nombre = form.cleaned_data['name']
    subject.curso = form.cleaned_data['course']
    subject.codigo = form.cleaned_data['code']
    subject.cuatrimestre = form.cleaned_data['quarter']
    subject.creditos = form.cleaned_data['credits']
    subject.web = form.cleaned_data['web']
    subject.duracion = form.cleaned_data['duration']
    subject.tipo_asignatura = form.cleaned_data['type']
    subject.departamento = form.cleaned_data['departament']

    return subject


def save(subject):
    subject.save()


def find_by_code(code):
    try:
        subject = Asignatura.objects.get(codigo=code)
    except Asignatura.DoesNotExist:
        subject = None
    return subject


def find_one(subject_id):
    try:
        subject = Asignatura.objects.get(id=subject_id)
    except Asignatura.DoesNotExist:
        subject = None
    return subject


def edit(form):
    subject = find_one(form.cleaned_data['id'])
    certifications_new = set(form.cleaned_data['certifications'])
    certification_subject = set(subject.titulacion_set.all())

    common = certifications_new.intersection(certification_subject)

    remove = certification_subject.difference(common)
    insert = certifications_new.difference(common)

    [subject.titulacion_set.add(certification) for certification in list(insert)]
    [subject.titulacion_set.remove(certification) for certification in list(remove)]

    return subject


def find_all():
    return Asignatura.objects.all()


# Returns the users subscribed to the logged lecturer's subjects
def lecturer_students(lecturer_id):
    students = [subject.alumno_set.all() for subject in get_lecturer_subjects(lecturer_id)]

    return list(set([item for sublist in students for item in sublist]))  # Merge lists inside and remove duplicates


def rollback(subject_create, subject_link, certifications):
    for subject in subject_link:
        [subject.titulacion_set.remove(certification) for certification in list(certifications)]

    for subject in subject_create:
        subject.delete()


def subject_students(subject, lecturer_id):
    return subject.alumno_set.all() if subject else get_lecturer_subjects(lecturer_id)


def get_form_data_xml(subject):
    data = {}
    if subject:
        data = {
            'name': subject['nombre'],
            'course': subject['curso'],
            'code': subject['codigo'],
            'quarter': subject['cuatrimestre'],
            'credits': subject['creditos'],
            'duration': subject['duracion'],
            'type': subject['tipo'],
        }

        try:
            data['web'] = subject['web']
        except KeyError:
            pass

        department = DepartmentService.find_by_code(subject['departamento'])
        data['departament'] = department.id

    return data


def get_form_data_csv(subject):
    data = {}
    if subject:
        data = {
            'name': subject[1],
            'course': subject[2],
            'code': subject[0],
            'quarter': subject[3],
            'credits': subject[4],
            'duration': subject[5],
            'type': subject[6],
        }
        try:
            data['web'] = subject[8]
        except IndexError:
            pass

        department = DepartmentService.find_by_code(subject[7])
        data['departament'] = department.id

    return data


def search(search_text):
    return Asignatura.objects.filter(
        Q(nombre__icontains=search_text) |
        Q(codigo__icontains=search_text)).order_by('nombre')


# TODO NO HA SIDO PROBADO (Revisar Carlos)
def get_student_subjects_search(student_id, search_text):
    student = Alumno.objects.get(id=student_id)
    return student.asignaturas.all().filter(
        Q(nombre__icontains=search_text) | Q(codigo__icontains=search_text)).order_by('nombre')


# TODO NO HA SIDO PROBADO (Revisar Carlos)
def get_lecturer_subjects_search(lecturer_id, search_text):
    return Asignatura.objects.filter(
        id__in=[a.asignatura.id for a in Imparteasignatura.objects.filter(
            profesor_id=lecturer_id & Q(asignatura_nombre__icontains=search_text) | Q(
                asignatura_codigo__icontains=search_text))]).order_by(
        'nombre')
