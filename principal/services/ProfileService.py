__author__ = 'Carlos'

from principal.models import Ficha, Alumno, Profesor
from principal.services import AddressService


def reconstruct_and_save(form, formset, student_id):
    student = Alumno.objects.get(id=student_id)
    if student.ficha:
        # Use existing data
        data = student.ficha
    else:
        data = Ficha()

    data.telefono = form.cleaned_data['phone1']
    # data.apellidos = form.cleaned_data['surname']
    data.movil = form.cleaned_data['phone2']
    data.fecha_nacimiento = form.cleaned_data['birth_date']
    form_photo = form.cleaned_data['photo']
    data.foto = data.foto if not form_photo else form_photo

    # Returns array -> [residence address, address while studying]
    addresses = AddressService.reconstruct_and_save(formset, student)
    data.direccion_residencia = addresses[0]
    data.direccion_estudios = addresses[1]

    # Save the student data
    data.save()

    # Update student data, id number and first_name (auth_user table)
    student.ficha = data
    student.dni = form.cleaned_data['id_number']
    student.first_name = form.cleaned_data['name']
    student.last_name = form.cleaned_data['surname']
    student.email = form.cleaned_data['email']

    student.save()


def get_form_data(student):
    data = {'name': student.first_name, 'surname': student.last_name}
    student_data = student.ficha

    if student_data:
        data['photo'] = student_data.foto
        data['email'] = student.email
        data['id_number'] = student.dni
        data['birth_date'] = student_data.fecha_nacimiento
        data['phone1'] = student_data.telefono
        data['phone2'] = student_data.movil

    return data


def get_formset_data(student):
    if student.ficha:
        residence_address = student.ficha.direccion_estudios
        studies_address = student.ficha.direccion_estudios

        # The first form is the residence address and the second form is the address while studying
        data = [{
            'address': residence_address.direccion,
            'province': residence_address.provincia,
            'location': residence_address.localizacion,
            'postal_code': residence_address.codigo_postal,
            'country': residence_address.pais
        },
            {
                'address': studies_address.direccion,
                'province': studies_address.provincia,
                'location': studies_address.localizacion,
                'postal_code': studies_address.codigo_postal,
                'country': studies_address.pais
            }]
        return data
    else:
        return {}


def build_initial_profile_data(lecturer):
    return {'name': lecturer.first_name, 'surname': lecturer.last_name, 'phone': lecturer.telefono,
            'office': lecturer.despacho, 'web': lecturer.web, 'category': lecturer.categoria, 'email': lecturer.email}


def update_profile(lecturer, form):
    lecturer.first_name = form.cleaned_data['name']
    lecturer.last_name = form.cleaned_data['surname']
    lecturer.telefono = form.cleaned_data['phone']
    lecturer.despacho = form.cleaned_data['office']
    lecturer.web = form.cleaned_data['web']
    lecturer.categoria = form.cleaned_data['category']
    lecturer.email = form.cleaned_data['email']

    lecturer.save()
