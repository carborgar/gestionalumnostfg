# -*- coding: utf-8 -*-
import smtplib

from django.contrib.auth.models import Permission
from django.test import TestCase
from principal.forms import *
from principal.models import *
from principal.services import DepartmentService, CertificationService, UserService, ImpartSubjectService, \
    AdministratorService
from gestionalumnos.settings import *
from django.core import mail
from django.test.utils import override_settings


class CertificationTestCase(TestCase):
    def setUp(self):
        # Departments
        self.department_lsi = Departamento.objects.create(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informaticos',
            web='http://www.lsi.us.es'
        )

        self.department_dte = Departamento.objects.create(
            codigo='2',
            nombre='Departamento de Tecnologia Electronica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )

        self.department_atc = Departamento.objects.create(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnologia de Computadores',
            web='http://www.atc.us.es/'
        )

        # Subjects
        self.subject_egc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Evolucion y gestion de la configuracion',
            curso='4',
            codigo='2050032',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=111',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        self.subject_rc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Redes de computadores',
            curso='2',
            codigo='2050013',
            creditos='6',
            duracion='C',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores',
            tipo_asignatura='OB',
            departamento=self.department_dte,
        )

        self.subject_cm = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Computacion Movil',
            curso='4',
            codigo='2060045',
            creditos='6',
            duracion='C',
            web='http://www.us.es/estudios/grados/plan_206/asignatura_2060045',
            tipo_asignatura='OP',
            departamento=self.department_atc,
        )

        self.subject_ispp = Asignatura.objects.create(
            cuatrimestre='2',
            nombre='Ingenieria del Software y Practica Profesional',
            curso='4',
            codigo='2050039',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        # Certifications
        self.certification_isw = Titulacion.objects.create(
            codigo='1',
            nombre='Grado en Informatica - Ingenieria del Software',
        )
        self.certification_isw.asignaturas.add(self.subject_rc, self.subject_ispp, self.subject_egc)

        self.certification_isc = Titulacion.objects.create(
            codigo='2',
            nombre='Grado en Informatica - Ingenieria de Computadores',
        )
        self.certification_isc.asignaturas.add(self.subject_rc)

        self.certification_iti = Titulacion.objects.create(
            codigo='3',
            nombre='Grado en Informatica - Tecnologias Informaticas',
        )
        self.certification_iti.asignaturas.add(self.subject_cm, self.subject_rc)

    def test_create_and_save_ok_1(self):
        data_form = {
            'code': '123456',
            'name': 'Grado en Informatica - Tecnologias Informaticas'
        }
        form = CertificationEditForm(data=data_form)
        self.assertEqual(form.is_valid(), True)
        certification = CertificationService.create_and_save(form)
        certification_bd = Titulacion.objects.get(codigo=123456)
        self.assertEqual(certification_bd, certification)

    def test_create_and_save_error_1(self):
        data_form = {
            'code': '1',
            'name': 'Grado en Informatica - Ingenieria del Software'
        }
        form = CertificationEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_find_all_ok_1(self):
        certifications = list(CertificationService.find_all())
        list_certifications = [self.certification_isc, self.certification_isw, self.certification_iti]
        self.assertListEqual(certifications, list_certifications)

    def test_find_by_code_ok_1(self):
        certification = CertificationService.find_by_code('2')
        self.assertEqual(certification, self.certification_isc)

    def test_find_by_code_error_1(self):
        certification = CertificationService.find_by_code('99')
        self.assertEqual(certification, None)

    def test_find_by_subject_ok_1(self):
        certifications = list(CertificationService.find_by_subject(self.subject_rc.id))
        list_certifications = [self.certification_isw, self.certification_isc, self.certification_iti]
        self.assertListEqual(certifications, list_certifications)

    def test_find_by_subject_ok_2(self):
        certifications = list(CertificationService.find_by_subject(self.subject_ispp.id))
        list_certifications = [self.certification_isw]
        self.assertListEqual(certifications, list_certifications)

    def test_find_by_subject_ok_3(self):
        certifications = list(CertificationService.find_by_subject('4874'))
        self.assertListEqual(certifications, [])

    def test_search_ok_1(self):
        certifications = list(CertificationService.search('Grado'))
        list_certifications = [self.certification_isc, self.certification_isw, self.certification_iti]
        self.assertListEqual(certifications, list_certifications)

    def test_search_ok_2(self):
        certifications = list(CertificationService.search('i'))
        list_certifications = [self.certification_isc, self.certification_isw, self.certification_iti]
        self.assertListEqual(certifications, list_certifications)

    def test_search_ok_3(self):
        certifications = list(CertificationService.search('Tecnologias'))
        list_certifications = [self.certification_iti]
        self.assertListEqual(certifications, list_certifications)

    def test_search_ok_4(self):
        certifications = list(CertificationService.search('z'))
        self.assertListEqual(certifications, [])

    def test_find_one_ok_1(self):
        certification = CertificationService.find_one(self.certification_isw.id)
        self.assertEqual(certification, self.certification_isw)


class AdministratorTestCase(TestCase):
    def setUp(self):
        # Administrators
        self.administrator1 = Administrador.objects.create(
            username='admin',
            is_staff=True,
            is_superuser=False
        )
        self.administrator1.set_password('admin')
        self.administrator1.user_permissions.add(Permission.objects.get(codename='administrator'))
        self.administrator1.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

    def test_find_one_ok_1(self):
        administrator = AdministratorService.find_one(self.administrator1.id)
        self.assertEqual(administrator, self.administrator1)


class DepartmentTestCase(TestCase):
    def setUp(self):
        # Departments
        self.department_lsi = Departamento.objects.create(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informaticos',
            web='http://www.lsi.us.es'
        )

        self.department_dte = Departamento.objects.create(
            codigo='2',
            nombre='Departamento de Tecnologia Electronica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )

        self.department_atc = Departamento.objects.create(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnologia de Computadores',
            web='http://www.atc.us.es/'
        )

    def test_reconstruct_and_save_ok_1(self):
        data_form = {
            'code': '4',
            'name': 'Departamento de Fisica',
            'web': 'http://www.fisica.us.es/'
        }
        form = DepartmentEditForm(data=data_form)
        self.assertEqual(form.is_valid(), True)
        department = DepartmentService.reconstruct_and_save(form)
        department_bd = Departamento.objects.get(codigo=4)
        self.assertEqual(department_bd, department)

    def test_reconstruct_and_save_ok_2(self):
        data_form = DepartmentService.get_form_data(self.department_lsi)
        data_form['name'] = 'Test'
        form = DepartmentEditForm(data=data_form)
        self.assertEqual(form.is_valid(), True)
        department = DepartmentService.reconstruct_and_save(form)
        department_bd = Departamento.objects.get(id=self.department_lsi.id)
        self.assertEqual(department_bd, department)
        self.assertEqual(department_bd.nombre, 'Test')

    def test_reconstruct_and_save_error_1(self):
        data_form = DepartmentService.get_form_data(self.department_lsi)
        data_form['code'] = '3'
        form = DepartmentEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_2(self):
        data_form = DepartmentService.get_form_data(self.department_lsi)
        data_form['id'] = '4944'
        form = DepartmentEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_3(self):
        data_form = DepartmentService.get_form_data(self.department_lsi)
        data_form['id'] = None
        form = DepartmentEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_find_all_ok_1(self):
        departments = list(DepartmentService.find_all())
        list_departments = [self.department_atc, self.department_lsi, self.department_dte]
        self.assertListEqual(departments, list_departments)

    def test_find_by_code_ok_1(self):
        department = DepartmentService.find_by_code('3')
        self.assertEqual(department, self.department_atc)

    def test_find_by_code_error_1(self):
        department = DepartmentService.find_by_code('99')
        self.assertEqual(department, None)

    def test_get_form_data_ok_1(self):
        data_form = DepartmentService.get_form_data(self.department_atc)
        data_form1 = {
            'id': self.department_atc.id,
            'code': self.department_atc.codigo,
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertDictEqual(data_form, data_form1)

    def test_get_form_data_error_1(self):
        data_form = DepartmentService.get_form_data(self.department_atc)
        data_form1 = {
            'id': self.department_atc.id,
            'code': '324245',
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertNotEqual(data_form, data_form1)

    def test_search_ok_1(self):
        departments = list(DepartmentService.search('Departamento'))
        list_departments = [self.department_atc, self.department_lsi, self.department_dte]
        self.assertListEqual(departments, list_departments)

    def test_search_ok_2(self):
        departments = list(DepartmentService.search('i'))
        list_departments = [self.department_atc, self.department_lsi, self.department_dte]
        self.assertListEqual(departments, list_departments)

    def test_search_ok_3(self):
        departments = list(DepartmentService.search('Lenguajes'))
        list_departments = [self.department_lsi]
        self.assertListEqual(departments, list_departments)

    def test_search_ok_4(self):
        departments = list(DepartmentService.search('zz'))
        self.assertListEqual(departments, [])

    def test_get_form_data_xml_ok_1(self):
        department = {
            'codigo': self.department_atc.codigo,
            'nombre': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        data_form = DepartmentService.get_form_data_xml(department)
        data_form1 = {
            'code': self.department_atc.codigo,
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertDictEqual(data_form, data_form1)

    def test_get_form_data_xml_error_1(self):
        department = {
            'codigo': '946514',
            'nombre': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        data_form = DepartmentService.get_form_data_xml(department)
        data_form1 = {
            'code': self.department_atc.codigo,
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertNotEqual(data_form, data_form1)

    def test_get_form_data_csv_ok_1(self):
        department = [
            self.department_atc.codigo,
            self.department_atc.nombre,
            self.department_atc.web
        ]
        data_form = DepartmentService.get_form_data_csv(department)
        data_form1 = {
            'code': self.department_atc.codigo,
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertDictEqual(data_form, data_form1)

    def test_get_form_data_csv_error_1(self):
        department = [
            '49498',
            self.department_atc.nombre,
            self.department_atc.web
        ]
        data_form = DepartmentService.get_form_data_csv(department)
        data_form1 = {
            'code': self.department_atc.codigo,
            'name': self.department_atc.nombre,
            'web': self.department_atc.web
        }
        self.assertNotEqual(data_form, data_form1)

    def test_rollback_ok_1(self):
        departments = list(DepartmentService.find_all())
        list_departments = [self.department_atc, self.department_lsi, self.department_dte]
        self.assertListEqual(departments, list_departments)
        DepartmentService.rollback(list_departments)
        departments = list(DepartmentService.find_all())
        self.assertListEqual([], departments)

    def test_find_one_ok_1(self):
        department = DepartmentService.find_one(self.department_atc.id)
        self.assertEqual(department, self.department_atc)


class ImpartSubjectTestCase(TestCase):
    def setUp(self):
        # Departments
        self.department_lsi = Departamento.objects.create(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informaticos',
            web='http://www.lsi.us.es'
        )

        self.department_dte = Departamento.objects.create(
            codigo='2',
            nombre='Departamento de Tecnologia Electronica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )

        self.department_atc = Departamento.objects.create(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnologia de Computadores',
            web='http://www.atc.us.es/'
        )

        # Subjects
        self.subject_egc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Evolucion y gestion de la configuracion',
            curso='4',
            codigo='2050032',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=111',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        self.subject_rc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Redes de computadores',
            curso='2',
            codigo='2050013',
            creditos='6',
            duracion='C',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores',
            tipo_asignatura='OB',
            departamento=self.department_dte,
        )

        self.subject_cm = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Computacion Movil',
            curso='4',
            codigo='2060045',
            creditos='6',
            duracion='C',
            web='http://www.us.es/estudios/grados/plan_206/asignatura_2060045',
            tipo_asignatura='OP',
            departamento=self.department_atc,
        )

        self.subject_ispp = Asignatura.objects.create(
            cuatrimestre='2',
            nombre='Ingenieria del Software y Practica Profesional',
            curso='4',
            codigo='2050039',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        # Lecturers
        self.lecturer_benavides = Profesor.objects.create(
            username='benavides',
            email='benavides@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954559897',
            despacho='F 0.48',
            web='http://www.lsi.us.es/~dbc/',
            first_name='David',
            last_name='Benavides Cuevas',
            tutoriaactivada=True,
            dni='55555555X'

        )
        self.lecturer_benavides.set_password('practica')
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_corchuelo = Profesor.objects.create(
            username='corchu',
            email='corchu@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954552770',
            despacho='F 1.63',
            first_name='Rafael',
            last_name='Corchuelo Gil',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=12',
            tutoriaactivada=True,
            dni='66666666X'

        )
        self.lecturer_corchuelo.set_password('practica')
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_muller = Profesor.objects.create(
            username='cmuller',
            email='cmuller@lsi.us.es',
            categoria='Becario FPI',
            telefono='954553868',
            despacho='F 0.43',
            first_name='Carlos',
            last_name='Muller Cejas',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=108',
            tutoriaactivada=True,
            dni='77777777X'

        )
        self.lecturer_muller.set_password('practica')
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_veronica = Profesor.objects.create(
            username='averonica',
            email='cmuller@lsi.us.es',
            categoria='Profesor Titular de Universidad ',
            telefono='954557095 ',
            despacho='G 1.69',
            first_name='Ana Veronica',
            last_name='Medina Rodriguez',
            web='http://www.dte.us.es/personal/vmedina/',
            tutoriaactivada=True,
            dni='88888888X'

        )
        self.lecturer_veronica.set_password('practica')
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

    def test_reconstruct_and_save_ok_1(self):
        data_form = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': self.lecturer_corchuelo.id,
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': 'Coordinador'
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), True)
        impart_subject = ImpartSubjectService.reconstruct_and_save(form)
        impart_subject_bd = Imparteasignatura.objects.get(profesor=self.lecturer_corchuelo,
                                                          asignatura=self.subject_ispp)
        self.assertEqual(impart_subject, impart_subject_bd)

    def test_reconstruct_and_save_error_1(self):
        data_form = {
            'subject_id': '',
            'lecturer_id': self.lecturer_corchuelo.id,
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': 'Coordinador'
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_2(self):
        data_form = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': '',
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': 'Coordinador'
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_3(self):
        data_form = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': self.lecturer_corchuelo.id,
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': ''
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_4(self):
        data_form = {
            'subject_id': '99854',
            'lecturer_id': self.lecturer_corchuelo.id,
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': ''
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_reconstruct_and_save_error_5(self):
        data_form = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': '74985',
            'lecturer': self.lecturer_corchuelo.first_name + self.lecturer_corchuelo.last_name,
            'position': ''
        }
        form = UserLinkSubjectForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_get_form_data_xml_ok_1(self):
        lecturer = {
            'uvus': self.lecturer_muller.username,
            'cargo': 'Profesor'
        }
        data_form = ImpartSubjectService.get_form_data_xml(lecturer, self.subject_ispp)
        data = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': self.lecturer_muller.id,
            'lecturer': self.lecturer_muller.first_name + self.lecturer_muller.last_name,
            'position': 'Profesor'
        }
        self.assertDictEqual(data_form, data)

    def test_get_form_data_xml_error_1(self):
        lecturer = {
            'uvus': self.lecturer_muller.username,
            'cargo': 'Profesor'
        }
        data_form = ImpartSubjectService.get_form_data_xml(lecturer, self.subject_ispp)
        data = {
            'subject_id': self.subject_ispp.id,
            'lecturer_id': '-1',
            'lecturer': self.lecturer_muller.first_name + self.lecturer_muller.last_name,
            'position': 'Profesor'
        }
        self.assertNotEqual(data_form, data)

    def test_get_form_data_xml_error_2(self):
        lecturer = {
            'uvus': self.lecturer_muller.username,
            'cargo': 'Profesor'
        }
        data_form = ImpartSubjectService.get_form_data_xml(lecturer, self.subject_ispp)
        data = {
            'subject_id': '-1',
            'lecturer_id': self.lecturer_muller.id,
            'lecturer': self.lecturer_muller.first_name + self.lecturer_muller.last_name,
            'position': 'Profesor'
        }
        self.assertNotEqual(data_form, data)

        # def test_get_form_data_csv_ok_1(self):
        #
        #     lecturer = [
        #         'Profesor',
        #         self.lecturer_muller.dni,
        #         self.lecturer_muller.last_name + "," + self.lecturer_muller.first_name,
        #         self.lecturer_muller.username,
        #         'null',
        #         'Coordinador'
        #     ]
        #     data_form = ImpartSubjectService.get_form_data_csv(lecturer, self.subject_ispp)
        #     data = {
        #         'subject_id': self.subject_ispp.id,
        #         'lecturer_id': self.lecturer_muller.id,
        #         'lecturer': "" + self.lecturer_muller.first_name + " " + self.lecturer_muller.last_name,
        #         'position': 'Profesor'
        #     }
        #     self.assertEqual(data_form, data)


class UserTestCase(TestCase):
    def setUp(self):
        # Departments
        self.department_lsi = Departamento.objects.create(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informaticos',
            web='http://www.lsi.us.es'
        )

        self.department_dte = Departamento.objects.create(
            codigo='2',
            nombre='Departamento de Tecnologia Electronica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )

        self.department_atc = Departamento.objects.create(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnologia de Computadores',
            web='http://www.atc.us.es/'
        )

        # Subjects
        self.subject_egc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Evolucion y gestion de la configuracion',
            curso='4',
            codigo='2050032',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=111',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        self.subject_rc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Redes de computadores',
            curso='2',
            codigo='2050013',
            creditos='6',
            duracion='C',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores',
            tipo_asignatura='OB',
            departamento=self.department_dte,
        )

        self.subject_cm = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Computacion Movil',
            curso='4',
            codigo='2060045',
            creditos='6',
            duracion='C',
            web='http://www.us.es/estudios/grados/plan_206/asignatura_2060045',
            tipo_asignatura='OP',
            departamento=self.department_atc,
        )

        self.subject_ispp = Asignatura.objects.create(
            cuatrimestre='2',
            nombre='Ingenieria del Software y Practica Profesional',
            curso='4',
            codigo='2050039',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        # Alumnos
        self.student_carborgar = Alumno.objects.create(
            username='carborgar',
            first_name='Carlos',
            last_name='Borja Garcia - Baquero',
            email='carborgar@alum.us.es',
            dni='47537495X'
        )
        self.student_carborgar.set_password('practica')
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_juamaiosu = Alumno.objects.create(
            username='juamaiosu',
            first_name='Juan Elias',
            last_name='Maireles Osuna',
            email='juamaiosu@alum.us.es',
            dni='47537560X'
        )
        self.student_juamaiosu.set_password('practica')
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_rubgombar = Alumno.objects.create(
            username='rubgombar',
            first_name='Ruben',
            last_name='Gomez Barrera',
            email='ruben@alum.us.es',
            dni='11111111X'
        )
        self.student_rubgombar.set_password('practica')
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_davjimvar = Alumno.objects.create(
            username='davjimvar',
            first_name='David',
            last_name='Jimenez Vargas',
            email='david@alum.us.es',
            dni='22222222X'
        )
        self.student_davjimvar.set_password('practica')
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_javrodleo = Alumno.objects.create(
            username='javrodleo',
            first_name='Javier',
            last_name='Rodriguez Leon',
            email='javier@alum.us.es',
            dni='33333333X'
        )
        self.student_javrodleo.set_password('practica')
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        # Lecturers
        self.lecturer_benavides = Profesor.objects.create(
            username='benavides',
            email='benavides@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954559897',
            despacho='F 0.48',
            web='http://www.lsi.us.es/~dbc/',
            first_name='David',
            last_name='Benavides Cuevas',
            tutoriaactivada=True,
            dni='55555555X'

        )
        self.lecturer_benavides.set_password('practica')
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_corchuelo = Profesor.objects.create(
            username='corchu',
            email='corchu@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954552770',
            despacho='F 1.63',
            first_name='Rafael',
            last_name='Corchuelo Gil',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=12',
            tutoriaactivada=True,
            dni='66666666X'

        )
        self.lecturer_corchuelo.set_password('practica')
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_muller = Profesor.objects.create(
            username='cmuller',
            email='cmuller@lsi.us.es',
            categoria='Becario FPI',
            telefono='954553868',
            despacho='F 0.43',
            first_name='Carlos',
            last_name='Muller Cejas',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=108',
            tutoriaactivada=True,
            dni='77777777X'

        )
        self.lecturer_muller.set_password('practica')
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_veronica = Profesor.objects.create(
            username='averonica',
            email='cmuller@lsi.us.es',
            categoria='Profesor Titular de Universidad ',
            telefono='954557095 ',
            despacho='G 1.69',
            first_name='Ana Veronica',
            last_name='Medina Rodriguez',
            web='http://www.dte.us.es/personal/vmedina/',
            tutoriaactivada=True,
            dni='88888888X'

        )
        self.lecturer_veronica.set_password('practica')
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.impart_ispp = Imparteasignatura.objects.create(
            cargo='Coordinador',
            profesor=self.lecturer_corchuelo,
            asignatura=self.subject_ispp
        )

        self.impart_ispp = Imparteasignatura.objects.create(
            cargo='Profesor',
            profesor=self.lecturer_muller,
            asignatura=self.subject_ispp
        )

        self.impart_egc = Imparteasignatura.objects.create(
            cargo='Coordinador',
            profesor=self.lecturer_benavides,
            asignatura=self.subject_egc
        )

        self.student_carborgar.asignaturas = [self.subject_egc, self.subject_ispp]

        self.student_juamaiosu.asignaturas = [self.subject_egc]

    def test_find_by_username_ok_1(self):
        user = UserService.find_by_username(self.student_carborgar.username)
        user_db = User.objects.get(username=self.student_carborgar.username)
        self.assertEqual(user, user_db)

    def test_find_by_username_error_1(self):
        user = UserService.find_by_username('ghslih')
        self.assertEqual(user, None)

    def test_delete_ok_1(self):
        username = self.student_carborgar.username
        UserService.delete(self.student_carborgar)
        error = False
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            error = True
        self.assertTrue(error)

    def test_rollback_users_ok_1(self):
        user_create = {self.lecturer_muller: 'password', self.lecturer_corchuelo: 'password'}
        len_list1 = len(list(UserService.find_all()))
        UserService.rollback_users(user_create)
        len_list2 = len(list(UserService.find_all()))
        self.assertIs(len_list1 - 2, len_list2)

    def test_rollback_ok_1(self):
        number_link_student_carborgar1 = len(list(self.student_carborgar.asignaturas.all()))
        number_link_student_juamaiosu1 = len(list(self.student_juamaiosu.asignaturas.all()))
        number_link_lecturer_benavides1 = len(list(self.lecturer_benavides.imparteasignatura_set.all()))
        student_link = [self.student_juamaiosu, self.student_carborgar]
        lecturer_link = [self.lecturer_benavides]
        user_create = [self.lecturer_veronica]
        username = self.lecturer_veronica.username
        UserService.rollback(user_create, student_link, lecturer_link, self.subject_egc.id)
        number_link_student_carborgar2 = len(list(self.student_carborgar.asignaturas.all()))
        number_link_student_juamaiosu2 = len(list(self.student_juamaiosu.asignaturas.all()))
        number_link_lecturer_benavides2 = len(list(self.lecturer_benavides.imparteasignatura_set.all()))
        self.assertEqual(number_link_student_carborgar1 - 1, number_link_student_carborgar2)
        self.assertEqual(number_link_student_juamaiosu1 - 1, number_link_student_juamaiosu2)
        self.assertEqual(number_link_lecturer_benavides1 - 1, number_link_lecturer_benavides2)
        error = False
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            error = True
        self.assertTrue(error)


class SubjectTestCase(TestCase):
    def setUp(self):
        # Departments
        self.department_lsi = Departamento.objects.create(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informaticos',
            web='http://www.lsi.us.es'
        )

        self.department_dte = Departamento.objects.create(
            codigo='2',
            nombre='Departamento de Tecnologia Electronica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )

        self.department_atc = Departamento.objects.create(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnologia de Computadores',
            web='http://www.atc.us.es/'
        )

        # Subjects
        self.subject_egc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Evolucion y gestion de la configuracion',
            curso='4',
            codigo='1',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=111',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        self.subject_rc = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Redes de computadores',
            curso='2',
            codigo='2',
            creditos='6',
            duracion='C',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores',
            tipo_asignatura='OB',
            departamento=self.department_dte,
        )

        self.subject_cm = Asignatura.objects.create(
            cuatrimestre='1',
            nombre='Computacion Movil',
            curso='4',
            codigo='3',
            creditos='6',
            duracion='C',
            web='http://www.us.es/estudios/grados/plan_206/asignatura_2060045',
            tipo_asignatura='OP',
            departamento=self.department_atc,
        )

        self.subject_ispp = Asignatura.objects.create(
            cuatrimestre='2',
            nombre='Ingenieria del Software y Practica Profesional',
            curso='4',
            codigo='4',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            tipo_asignatura='OB',
            departamento=self.department_lsi,
        )

        # Alumnos
        self.student_carborgar = Alumno.objects.create(
            username='carborgar',
            first_name='Carlos',
            last_name='Borja Garcia - Baquero',
            email='carborgar@alum.us.es',
            dni='47537495X'
        )
        self.student_carborgar.set_password('practica')
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_carborgar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_juamaiosu = Alumno.objects.create(
            username='juamaiosu',
            first_name='Juan Elias',
            last_name='Maireles Osuna',
            email='juamaiosu@alum.us.es',
            dni='47537560X'
        )
        self.student_juamaiosu.set_password('practica')
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_juamaiosu.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_rubgombar = Alumno.objects.create(
            username='rubgombar',
            first_name='Ruben',
            last_name='Gomez Barrera',
            email='ruben@alum.us.es',
            dni='11111111X'
        )
        self.student_rubgombar.set_password('practica')
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_rubgombar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_davjimvar = Alumno.objects.create(
            username='davjimvar',
            first_name='David',
            last_name='Jimenez Vargas',
            email='david@alum.us.es',
            dni='22222222X'
        )
        self.student_davjimvar.set_password('practica')
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_davjimvar.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        self.student_javrodleo = Alumno.objects.create(
            username='javrodleo',
            first_name='Javier',
            last_name='Rodriguez Leon',
            email='javier@alum.us.es',
            dni='33333333X'
        )
        self.student_javrodleo.set_password('practica')
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='alumno'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        self.student_javrodleo.user_permissions.add(Permission.objects.get(codename='view_subject_details'))

        # Lecturers
        self.lecturer_benavides = Profesor.objects.create(
            username='benavides',
            email='benavides@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954559897',
            despacho='F 0.48',
            web='http://www.lsi.us.es/~dbc/',
            first_name='David',
            last_name='Benavides Cuevas',
            tutoriaactivada=True,
            dni='55555555X'

        )
        self.lecturer_benavides.set_password('practica')
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_benavides.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_corchuelo = Profesor.objects.create(
            username='corchu',
            email='corchu@us.es',
            categoria='Profesor Titular de Universidad',
            telefono='954552770',
            despacho='F 1.63',
            first_name='Rafael',
            last_name='Corchuelo Gil',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=12',
            tutoriaactivada=True,
            dni='66666666X'

        )
        self.lecturer_corchuelo.set_password('practica')
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_corchuelo.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_muller = Profesor.objects.create(
            username='cmuller',
            email='cmuller@lsi.us.es',
            categoria='Becario FPI',
            telefono='954553868',
            despacho='F 0.43',
            first_name='Carlos',
            last_name='Muller Cejas',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=108',
            tutoriaactivada=True,
            dni='77777777X'

        )
        self.lecturer_muller.set_password('practica')
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_muller.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.lecturer_veronica = Profesor.objects.create(
            username='averonica',
            email='cmuller@lsi.us.es',
            categoria='Profesor Titular de Universidad ',
            telefono='954557095 ',
            despacho='G 1.69',
            first_name='Ana Veronica',
            last_name='Medina Rodriguez',
            web='http://www.dte.us.es/personal/vmedina/',
            tutoriaactivada=True,
            dni='88888888X'

        )
        self.lecturer_veronica.set_password('practica')
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='profesor'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        self.lecturer_veronica.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))

        self.impart_ispp_corchu = Imparteasignatura.objects.create(
            cargo='Coordinador',
            profesor=self.lecturer_corchuelo,
            asignatura=self.subject_ispp
        )

        self.impart_ispp_muller = Imparteasignatura.objects.create(
            cargo='Profesor',
            profesor=self.lecturer_muller,
            asignatura=self.subject_ispp
        )

        self.impart_ispp_benavides = Imparteasignatura.objects.create(
            cargo='Coordinador',
            profesor=self.lecturer_benavides,
            asignatura=self.subject_ispp
        )

        self.impart_egc_benavides = Imparteasignatura.objects.create(
            cargo='Coordinador',
            profesor=self.lecturer_benavides,
            asignatura=self.subject_egc
        )

        self.student_carborgar.asignaturas = [self.subject_egc, self.subject_ispp]

        self.student_juamaiosu.asignaturas = [self.subject_egc]

    def test_get_student_subjects_ok_1(self):
        subjects = list(SubjectService.get_student_subjects(self.student_carborgar.id))
        subjects1 = [self.subject_egc, self.subject_ispp]
        self.assertListEqual(subjects, subjects1)

    def test_get_lecturer_subjects_ok_1(self):
        subjects = list(SubjectService.get_lecturer_subjects(self.lecturer_benavides.id))
        subjects1 = [self.subject_egc, self.subject_ispp]
        self.assertListEqual(subjects, subjects1)

    def test_create_and_save_ok_1(self):
        data_form = {
            'name': 'Prueba',
            'course': '1',
            'code': '5',
            'quarter': '1',
            'credits': '6',
            'web': 'http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            'duration': 'C',
            'type': 'OB',
            'departament': self.department_lsi.id,
        }
        form = SubjectEditForm(data=data_form)
        self.assertEqual(form.is_valid(), True)
        subject = SubjectService.create(form)
        SubjectService.save(subject)
        subject_bd = Asignatura.objects.get(codigo=subject.codigo)
        self.assertEqual(subject, subject_bd)

    def test_create_and_save_error_1(self):
        data_form = {
            'name': 'Prueba',
            'course': '1',
            'code': '4',
            'quarter': '1',
            'credits': '6',
            'web': 'http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            'duration': 'C',
            'type': 'OB',
            'departament': self.department_lsi.id,
        }
        form = SubjectEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_create_and_save_error_2(self):
        data_form = {
            'name': 'Prueba',
            'course': '10',
            'code': '5',
            'quarter': '1',
            'credits': '6',
            'web': 'http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            'duration': 'C',
            'type': 'OB',
            'departament': self.department_lsi.id,
        }
        form = SubjectEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_create_and_save_error_3(self):
        data_form = {
            'name': 'Prueba',
            'course': '1',
            'code': '5',
            'quarter': '8',
            'credits': '6',
            'web': 'http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            'duration': 'C',
            'type': 'OB',
            'departament': self.department_lsi.id,
        }
        form = SubjectEditForm(data=data_form)
        self.assertEqual(form.is_valid(), False)

    def test_find_by_code_ok_1(self):
        subject = SubjectService.find_by_code(self.subject_ispp.codigo)
        self.assertEqual(subject, self.subject_ispp)

    def test_find_by_code_error_1(self):
        subject = SubjectService.find_by_code('5')
        self.assertEqual(subject, None)

    def test_find_one_ok_1(self):
        subject = SubjectService.find_one(self.subject_ispp.id)
        self.assertEqual(subject, self.subject_ispp)

    def test_find_one_error_1(self):
        subject = SubjectService.find_one('-1')
        self.assertEqual(subject, None)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class EmailTestCase(TestCase):

    def test_send_email(self):
        try:
            mail_sent_success = mail.send_mail('Test',
                                               'Test',
                                               EMAIL_HOST_USER, [EMAIL_HOST_USER],
                                               fail_silently=True)
            self.assertEqual(mail_sent_success, 1)
        except Exception:
            self.assertEqual(False, True, 'No se ha podido enviar el correo')
