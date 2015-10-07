# -*- coding: utf-8 -*-
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from __future__ import unicode_literals
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import (
    AbstractBaseUser
)
from django.utils.translation import ugettext_lazy as _
import datetime
import uuid
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Alumno(User):
    # -------------- Relationships -------------------
    ficha = models.OneToOneField('Ficha', db_column='idFicha', null=True)
    asignaturas = models.ManyToManyField('Asignatura')
    dni = models.CharField(max_length=9, unique=True)

    class Meta:
        ordering = ['last_name']
        db_table = 'alumno'
        permissions = (
            ('alumno', 'Alumno'),
        )

    def __str__(self):
        return self.last_name + ', ' + self.first_name


@python_2_unicode_compatible
class Asignatura(models.Model):
    TIPO_ASIGNATURA_CHOICES = (
        ('FB', _('Basic formation')),
        ('OB', _('Compulsory')),
        ('OP', _('Optional')),
        ('TFG', _('Final degree thesis')),

    )

    DURACION_CHOICES = (
        ('A', _('Annual')),
        ('C', _('Quarterly')),
    )
    id = models.AutoField(db_column='idAsignatura', primary_key=True)
    cuatrimestre = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    nombre = models.CharField(max_length=100)
    curso = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    codigo = models.CharField(max_length=255, unique=True)
    creditos = models.FloatField()
    duracion = models.CharField(max_length=1, choices=DURACION_CHOICES)
    web = models.CharField(max_length=150)
    tipo_asignatura = models.CharField(db_column='tipoAsignatura', max_length=3, choices=TIPO_ASIGNATURA_CHOICES)

    # -------------- Relationships -------------------
    departamento = models.ForeignKey('Departamento', db_column='departamento')

    class Meta:
        db_table = 'asignatura'
        permissions = (('view_subject_details', 'Can view subject details'),)

    def __str__(self):
        return self.nombre


@python_2_unicode_compatible
class Departamento(models.Model):
    id = models.AutoField(db_column='idDepartamento', primary_key=True)
    codigo = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    web = models.CharField(max_length=255)

    class Meta:
        db_table = 'departamento'

    def __str__(self):
        return self.nombre


class Direccion(models.Model):
    id = models.AutoField(db_column='idDireccion', primary_key=True)
    direccion = models.CharField(max_length=100)
    localizacion = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    provincia = models.CharField(max_length=50)
    codigo_postal = models.IntegerField(db_column='codigoPostal')

    class Meta:
        db_table = 'direccion'


class Ficha(models.Model):
    id = models.AutoField(db_column='IdFicha', primary_key=True)
    fecha_actualizacion = models.DateField(db_column='fechaActualizacion', auto_now=True)
    telefono = models.CharField(max_length=9)
    movil = models.CharField(max_length=9)
    foto = models.ImageField(upload_to='static/student/', null=True, default='static/student/default.jpg')
    fecha_nacimiento = models.DateField(db_column='fechaNacimiento')

    # -------------- Relationships -------------------
    direccion_residencia = models.ForeignKey(Direccion, db_column='idDirecciona', related_name='direccion_residencia')
    direccion_estudios = models.ForeignKey(Direccion, db_column='idDireccionb', related_name='direccion_estudios')

    class Meta:
        db_table = 'ficha'

    def save(self, *args, **kwargs):
        # delete old file when replacing by updating the file
        try:
            this = Ficha.objects.get(id=self.id)
            if this.foto != self.foto and this.foto.name != 'static/student/default.jpg':
                this.foto.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case

        super(Ficha, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Imparteasignatura(models.Model):
    cargo = models.CharField(max_length=255)

    # -------------- Relationships -------------------
    profesor = models.ForeignKey('Profesor', db_column='profesor')
    asignatura = models.ForeignKey(Asignatura, db_column='asignatura')

    class Meta:
        db_table = 'imparteasignatura'
        unique_together = (('profesor', 'asignatura'),)
        permissions = (
            ('view_certification_list', 'Can view certifications list'),
        )

    def __str__(self):
        return '%s  (%s)' % (self.profesor, self.cargo)


class Noticia(models.Model):
    id = models.AutoField(db_column='idNoticia', primary_key=True)
    titulo = models.CharField(max_length=100, null=False, blank=False)
    texto = models.TextField(max_length=255, null=False, blank=False)
    fecha_inicio = models.DateField(db_column='fechaIni', auto_now_add=True, null=False)
    fecha_modificacion = models.DateField(db_column='fechaMod', auto_now=True, null=False)

    # -------------- Relationships -------------------
    asignatura = models.ForeignKey(Asignatura, db_column='asignatura')
    profesor = models.ForeignKey('Profesor', db_column='profesor')

    class Meta:
        db_table = 'noticia'
        ordering = ['-fecha_inicio', '-id']


class Observacion(models.Model):
    id = models.AutoField(db_column='idObservacion', primary_key=True)
    descripcion = models.CharField(max_length=255)
    fecha = models.DateField(auto_now_add=True)

    # -------------- Relationships -------------------
    profesor = models.ForeignKey('Profesor', db_column='profesor')
    alumno = models.ForeignKey(Alumno, db_column='alumno')
    asignatura = models.ForeignKey(Asignatura, db_column='asignatura')

    class Meta:
        db_table = 'observacion'


@python_2_unicode_compatible
class Peticioncita(models.Model):
    ESTADO_PETICION = (
        ('EC', _('Pending')),
        ('DE', _('Rejected')),
        ('CA', _('Cancelled')),
        ('AC', _('Accepted')),
    )
    idcita = models.AutoField(db_column='idCita', primary_key=True)
    motivo = models.CharField(max_length=255)
    estado = models.CharField(max_length=15, choices=ESTADO_PETICION)
    fechacita = models.DateTimeField(db_column='fechaCita')
    fechacitafin = models.DateTimeField(db_column='fechaCitaFin')
    motivocancelacion = models.CharField(db_column='motivoCancelacion', max_length=255, null=True)
    activation_hash = models.UUIDField(default=uuid.uuid4, editable=False, null=False, blank=False, unique=True)

    # -------------- Relationships -------------------
    alumno = models.ForeignKey(Alumno, db_column='alumno')
    profesor = models.ForeignKey('Profesor', db_column='profesor')

    class Meta:
        db_table = 'peticioncita'
        permissions = (
            ('view_tutorial_request_list', 'Can view tutorial request list'),
        )

    def __str__(self):
        return '%s - %s %s' % (
            datetime.datetime.strftime(self.fechacita, '%H:%M'), datetime.datetime.strftime(self.fechacitafin, '%H:%M'),
            self.alumno)


@python_2_unicode_compatible
class Profesor(User):
    categoria = models.CharField(max_length=100, null=True)
    telefono = models.IntegerField(null=True)
    despacho = models.CharField(max_length=100, null=True)
    web = models.URLField(max_length=100, null=True)
    motivotutorias = models.CharField(db_column='motivoTutorias', max_length=100, null=True)
    tutoriaactivada = models.BooleanField(db_column='tutoriaActivada', default=True)
    dni = models.CharField(max_length=9, unique=True)
    # intervalo = models.IntegerField(null=False, default=30)
    # -------------- Relationships -------------------
    # usuario = models.ForeignKey('Usuario', db_column='idUsuario', primary_key=True)

    class Meta:
        permissions = (
            ("profesor", "Profesor"),
        )
        db_table = 'profesor'

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def tutoria_days(self):
        tutorials = [tutorial.dia for tutorial in self.tutoria_set.all()]
        return list(set(tutorials))


@python_2_unicode_compatible
class Titulacion(models.Model):
    id = models.AutoField(db_column='idTitulacion', primary_key=True)
    codigo = models.CharField(max_length=255, unique=True)
    nombre = models.CharField(max_length=255)
    asignaturas = models.ManyToManyField(Asignatura)

    class Meta:
        db_table = 'titulacion'

    def __str__(self):
        return self.nombre


class Tutoria(models.Model):
    DIAS_SEMANA = (
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
    )
    id = models.AutoField(db_column='idTutoria', primary_key=True)
    horainicio = models.TimeField(db_column='horaInicio')
    horafin = models.TimeField(db_column='horaFin')
    dia = models.PositiveIntegerField(choices=DIAS_SEMANA, validators=[MinValueValidator(1), MaxValueValidator(5)])

    # -------------- Relationships -------------------
    profesor = models.ForeignKey(Profesor, db_column='idUsuario')

    class Meta:
        db_table = 'tutoria'
        ordering = ['horainicio']


class Administrador(User):
    class Meta:
        permissions = (
            ('administrator', 'Administrator'),
        )
        db_table = 'administrador'
