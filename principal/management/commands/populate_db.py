# -*- coding: utf-8 -*-
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission

from principal.models import Alumno
from principal.models import Asignatura
from principal.models import Departamento
from principal.models import Direccion
from principal.models import Ficha
from principal.models import Imparteasignatura
from principal.models import Noticia
from principal.models import Observacion
from principal.models import Peticioncita
from principal.models import Profesor
from principal.models import Titulacion
from principal.models import Tutoria
from principal.models import Administrador


# Los archivos que se encuentren en el paquete commands, se podrán llamar
# desde manage.py, de forma que para popular la base de datos debemos hacer
# 'manage.py populate_db'

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    @staticmethod
    def insert_test_data(self):
        print('Creating test data...')
        # Direcciones
        direccion1 = Direccion(
            direccion='Calle Huerta Grande, 57',
            localizacion='Alcalá del Río',
            pais='España',
            provincia='Sevilla',
            codigo_postal='41200'
        )
        direccion1.save()

        direccion2 = Direccion(
            direccion='Av. Reina Mercedes',
            localizacion='Sevilla',
            pais='España',
            provincia='Sevilla',
            codigo_postal='41012'
        )
        direccion2.save()

        # Fichas
        ficha_carlos = Ficha(
            telefono='955650871',
            movil='640263470',
            fecha_nacimiento=datetime.date(1993, 0o5, 30),
            direccion_residencia=direccion1,
            direccion_estudios=direccion2
        )
        ficha_carlos.save()

        # Alumnos
        alum1 = Alumno(
            username='carborgar',
            first_name='Carlos',
            last_name='Borja García - Baquero',
            email='carborgar@alum.us.es',
            ficha=ficha_carlos,
            dni='47537495X'
        )
        alum1.set_password('practica')
        alum1.save()
        alum1.user_permissions.add(Permission.objects.get(codename='alumno'))
        alum1.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        alum1.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        alum1.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        alum1.save()

        alum2 = Alumno(
            username='juamaiosu',
            first_name='Juan Elias',
            last_name='Maireles Osuna',
            email='juamaiosu@alum.us.es',
            dni='47537560X'
        )
        alum2.set_password('practica')
        alum2.save()
        alum2.user_permissions.add(Permission.objects.get(codename='alumno'))
        alum2.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        alum2.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        alum2.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        alum2.save()

        alum3 = Alumno(
            username='rubgombar',
            first_name='Rubén',
            last_name='Gómez Barrera',
            email='ruben@alum.us.es',
            dni='11111111X'
        )
        alum3.set_password('practica')
        alum3.save()
        alum3.user_permissions.add(Permission.objects.get(codename='alumno'))
        alum3.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        alum3.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        alum3.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        alum3.save()

        alum4 = Alumno(
            username='davjimvar',
            first_name='David',
            last_name='Jiménez Vargas',
            email='david@alum.us.es',
            dni='22222222X'
        )
        alum4.set_password('practica')
        alum4.save()
        alum4.user_permissions.add(Permission.objects.get(codename='alumno'))
        alum4.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        alum4.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        alum4.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        alum4.save()

        alum5 = Alumno(
            username='frarodleo1',
            first_name='Javier',
            last_name='Rodríguez León',
            email='javier@alum.us.es',
            dni='33333333X'
        )
        alum5.set_password('practica')
        alum5.save()
        alum5.user_permissions.add(Permission.objects.get(codename='alumno'))
        alum5.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        alum5.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        alum5.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        alum5.save()

        # Profesores
        prof1 = Profesor(
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
        prof1.set_password('practica')
        prof1.save()
        prof1.user_permissions.add(Permission.objects.get(codename='profesor'))
        prof1.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        prof1.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        prof1.save()

        prof2 = Profesor(
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
        prof2.set_password('practica')
        prof2.save()
        prof2.user_permissions.add(Permission.objects.get(codename='profesor'))
        prof2.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        prof2.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        prof2.save()

        prof_muller = Profesor(
            username='cmuller',
            email='cmuller@lsi.us.es',
            categoria='Becario FPI',
            telefono='954553868',
            despacho='F 0.43',
            first_name='Carlos',
            last_name='Muller Cejás',
            web='https://www.lsi.us.es/personal/pagina_personal.php?id=108',
            tutoriaactivada=True,
            dni='77777777X'

        )
        prof_muller.set_password('practica')
        prof_muller.save()
        prof_muller.user_permissions.add(Permission.objects.get(codename='profesor'))
        prof_muller.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        prof_muller.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        prof_muller.save()

        prof_veronica = Profesor(
            username='averonica',
            email='cmuller@lsi.us.es',
            categoria='Profesor Titular de Universidad ',
            telefono='954557095 ',
            despacho='G 1.69',
            first_name='Ana Verónica',
            last_name='Medina Rodríguez',
            web='http://www.dte.us.es/personal/vmedina/',
            tutoriaactivada=True,
            dni='88888888X'

        )
        prof_veronica.set_password('practica')
        prof_veronica.save()
        prof_veronica.user_permissions.add(Permission.objects.get(codename='profesor'))
        prof_veronica.user_permissions.add(Permission.objects.get(codename='view_certification_list'))
        prof_veronica.user_permissions.add(Permission.objects.get(codename='view_tutorial_request_list'))
        prof_veronica.save()

        # Departamentos
        departamento_lsi = Departamento(
            codigo='1',
            nombre='Departamento de Lenguajes y Sistemas Informáticos',
            web='http://www.lsi.us.es'
        )
        departamento_lsi.save()

        departamento_dte = Departamento(
            codigo='2',
            nombre='Departamento de Tecnología Electrónica',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores'
        )
        departamento_dte.save()

        departamento_atc = Departamento(
            codigo='3',
            nombre='Departamento de Arquitectura y Tecnología de Computadores',
            web='http://www.atc.us.es/'
        )
        departamento_atc.save()

        # Asignaturas
        asignatura_egc = Asignatura(
            cuatrimestre='1',
            nombre='Evolución y gestión de la configuración',
            curso='4',
            codigo='2050032',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=111',
            tipo_asignatura='OB',
            departamento=departamento_lsi,
        )
        asignatura_egc.save()

        asignatura_rc = Asignatura(
            cuatrimestre='1',
            nombre='Redes de computadores',
            curso='2',
            codigo='2050013',
            creditos='6',
            duracion='C',
            web='https://www.dte.us.es/docencia/etsii/gii-is/redes-de-computadores',
            tipo_asignatura='OB',
            departamento=departamento_dte,
        )
        asignatura_rc.save()

        asignatura_cm = Asignatura(
            cuatrimestre='1',
            nombre='Computación Móvil',
            curso='4',
            codigo='2060045',
            creditos='6',
            duracion='C',
            web='http://www.us.es/estudios/grados/plan_206/asignatura_2060045',
            tipo_asignatura='OP',
            departamento=departamento_atc,
        )
        asignatura_cm.save()

        asignatura_ispp = Asignatura(
            cuatrimestre='2',
            nombre='Ingeniería del Software y Práctica Profesional',
            curso='4',
            codigo='2050039',
            creditos='6',
            duracion='C',
            web='http://www.lsi.us.es/docencia/pagina_asignatura.php?id=110',
            tipo_asignatura='OB',
            departamento=departamento_lsi,
        )
        asignatura_ispp.save()

        titulacion_isw = Titulacion(
            codigo='1',
            nombre='Grado en Informática - Ingeniería del Software',
        )
        titulacion_isw.save()
        titulacion_isw.asignaturas.add(asignatura_rc, asignatura_ispp, asignatura_egc)
        titulacion_isw.save()

        titulacion_isc = Titulacion(
            codigo='2',
            nombre='Grado en Informática - Ingeniería de Computadores',
        )
        titulacion_isc.save()
        titulacion_isc.asignaturas.add(asignatura_rc)
        titulacion_isc.save()

        titulacion_iti = Titulacion(
            codigo='3',
            nombre='Grado en Informática - Tecnologías Informáticas',
        )
        titulacion_iti.save()
        titulacion_iti.asignaturas.add(asignatura_cm, asignatura_rc)
        titulacion_iti.save()

        imparte_ispp = Imparteasignatura(
            cargo='Coordinador',
            profesor=prof2,
            asignatura=asignatura_ispp
        )
        imparte_ispp.save()

        imparte_ispp = Imparteasignatura(
            cargo='Profesor',
            profesor=prof_muller,
            asignatura=asignatura_ispp
        )
        imparte_ispp.save()

        imparte_egc = Imparteasignatura(
            cargo='Coordinador',
            profesor=prof1,
            asignatura=asignatura_egc
        )
        imparte_egc.save()

        alum1.asignaturas = [asignatura_egc, asignatura_ispp]
        alum1.save()

        alum2.asignaturas = [asignatura_egc]
        alum2.save()

        # Peticiones

        Peticioncita.objects.create(
            motivo='Necesito esta cita porque...',
            estado='AC',
            fechacita=datetime.datetime(2015, 0o7, 13, 10, 00),
            fechacitafin=datetime.datetime(2015, 0o7, 13, 10, 30),
            alumno=alum1,
            profesor=prof1
        )

        Peticioncita.objects.create(
            motivo='Necesito esta cita 2 porque...',
            estado='AC',
            fechacita=datetime.datetime(2015, 0o7, 13, 11, 00),
            fechacitafin=datetime.datetime(2015, 0o7, 13, 11, 30),
            alumno=alum1,
            profesor=prof1
        )

        Peticioncita.objects.create(
            motivo='Necesito esta cita 3 porque...',
            estado='AC',
            fechacita=datetime.datetime(2015, 0o7, 15, 1, 30),
            fechacitafin=datetime.datetime(2015, 0o7, 15, 11, 00),
            alumno=alum3,
            profesor=prof1
        )

        Peticioncita.objects.create(
            motivo='Necesito esta cita 4 porque...',
            estado='AC',
            fechacita=datetime.datetime(2015, 0o7, 15, 11, 00),
            fechacitafin=datetime.datetime(2015, 0o7, 15, 11, 30),
            alumno=alum2,
            profesor=prof1
        )

        Peticioncita.objects.create(
            motivo='Necesito esta cita 5 porque...',
            estado='AC',
            fechacita=datetime.datetime(2015, 0o7, 13, 11, 00),
            fechacitafin=datetime.datetime(2015, 0o7, 13, 11, 30),
            alumno=alum2,
            profesor=prof1
        )

        Noticia.objects.create(
            titulo='Esta es la noticia 1',
            texto='Lorem ipsum dolor sit amet, nonummy ligula volutpat hac integer nonummy. Suspendisse ultricies, congue etiam tellus, erat libero, nulla eleifend, mauris pellentesque. Suspendisse integer praesent vel, integer gravida mauris, fringilla vehicula lacinia non',
            asignatura=asignatura_egc,
            profesor=prof1
        )

        Noticia.objects.create(
            titulo='Esta es la noticia 2, que lleva un enlace',
            texto='Lorem ipsum dolor sit amet y lleva un enlace escrito normal (copiad y pegado) https://www.google.es/?gws_rd=sslm',
            asignatura=asignatura_ispp,
            profesor=prof2
        )

        Noticia.objects.create(
            titulo='Esta es la noticia 3',
            texto='Que tiene poco contenido',
            asignatura=asignatura_egc,
            profesor=prof1
        )

        Observacion.objects.create(
            descripcion='Es un gran estudiante',
            profesor=prof1,
            alumno=alum1,
            asignatura=asignatura_egc
        )

        Observacion.objects.create(
            descripcion='Faltó a clase el jueves pasado',
            profesor=prof1,
            alumno=alum1,
            asignatura=asignatura_egc
        )

        Observacion.objects.create(
            descripcion='Sigue faltando a clase.',
            profesor=prof2,
            alumno=alum1,
            asignatura=asignatura_ispp
        )
        print('Creating test data...OK\n')

    @staticmethod
    def insert_production_data(self):
        print('\nCreating administrators...')
        # Administrators
        admin = Administrador(
            username='admin',
            is_staff=True,
            is_superuser=False
        )
        admin.set_password('practica')
        admin.save()
        admin.user_permissions.add(Permission.objects.get(codename='administrator'))
        admin.user_permissions.add(Permission.objects.get(codename='view_subject_details'))
        admin.save()
        print('Creating administrators...OK\n')

    @staticmethod
    def clean_tables(self):
        print('Dropping tables...')
        Alumno.objects.all().delete()
        Asignatura.objects.all().delete()
        Departamento.objects.all().delete()
        Direccion.objects.all().delete()
        Ficha.objects.all().delete()
        Imparteasignatura.objects.all().delete()
        Noticia.objects.all().delete()
        Observacion.objects.all().delete()
        Peticioncita.objects.all().delete()
        Profesor.objects.all().delete()
        Observacion.objects.all().delete()
        Titulacion.objects.all().delete()
        Tutoria.objects.all().delete()
        Administrador.objects.all().delete()
        print('Dropping tables...OK')

    def add_arguments(self, parser):

        parser.add_argument('--production_new_db_admin',
                            action='store_true',
                            dest='production_new_db_admin',
                            default=False,
                            help='Create database structure only (with an administrator')

    def handle(self, *args, **options):
        self.clean_tables(self)
        self.insert_production_data(self)

        if not options['production_new_db_admin']:
            self.insert_test_data(self)