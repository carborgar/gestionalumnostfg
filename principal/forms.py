# -*- coding: utf-8 -*-

from django import forms
from principal.validators import username_validator
from principal.services import CertificationService, DepartmentService, UserService, SubjectService
from principal.models import Departamento, Titulacion, Alumno
import datetime
from django.contrib.auth.models import User
from principal.models import Profesor, Tutoria, Peticioncita, Imparteasignatura
from principal.services import PeticionCitaService, StudentService, LecturerService

from django.utils.translation import ugettext as _
from django.contrib.auth.forms import PasswordChangeForm
import re


class PeticionCitaForm(forms.Form):
    subject = forms.IntegerField(label=_('Subject'),
                                 widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                 required=True)
    lecturer_id = forms.IntegerField(label=_('Lecturer'),
                                     widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
                                     required=True)


class CertificationEditForm(forms.Form):
    code = forms.DecimalField(
        label='code',
        required=True,
        max_digits=254,
        min_value=0,
        decimal_places=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '0',
                'data-maxlength': '254',
            }
        )
    )

    name = forms.CharField(
        label='name',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    def clean(self):
        code = self.cleaned_data.get('code')
        if code is not None:
            certification = CertificationService.find_by_code(code)
            if certification is not None:
                self.add_error('code', _("There cannot be two certifications with the same code"))

        return self.cleaned_data


class DepartmentEditForm(forms.Form):
    id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    code = forms.DecimalField(
        label='code',
        required=True,
        max_digits=254,
        min_value=0,
        decimal_places=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '0',
                'data-maxlength': '254',
            }
        )
    )

    name = forms.CharField(
        label='name',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    web = forms.URLField(
        label='web',
        required=True,
        max_length=254,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    def clean(self):

        id_departament = self.cleaned_data.get('id')
        code = self.cleaned_data.get('code')

        if code:
            departament = DepartmentService.find_by_code(code)
            # Al editar puede existir otro departamento con el mismo codigo
            if id_departament:
                if departament.id != id_departament:
                    self.add_error('code', _("There cannot be two certifications with the same code"))
            else:
                if departament:
                    self.add_error('code', _("There cannot be two certifications with the same code"))

        return self.cleaned_data


class UserEditForm(forms.Form):
    RADIO_CHOICES = (
        ('st', _("Student")),
        ('le', _("Lecturer")),
    )

    first_name = forms.CharField(
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    last_name = forms.CharField(
        required=True,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '30',
            }
        )
    )

    user = forms.CharField(
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    dni = forms.CharField(
        required=True,
        max_length=9,
        validators=[username_validator],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '9',
                'pattern': '^\d{8}[A-Z]$'
            }
        )
    )

    type = forms.ChoiceField(
        required=True,
        choices=RADIO_CHOICES,
        widget=forms.RadioSelect(
            attrs={
                'required': 'required',
            }
        )
    )

    email = forms.EmailField(
        required=False,
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'maxlength': '254',
            }
        )
    )

    def clean(self):

        username = self.cleaned_data.get('user')
        if username is not None:
            user = UserService.find_by_username(username)
            if user is not None:
                self.add_error('user', _("There cannot be two users with the same username"))
            else:
                dni = self.cleaned_data.get('dni')
                user = StudentService.find_by_dni(dni)
                if user is not None:
                    self.add_error('dni', _("There cannot be two users with the same ID number"))
                else:
                    user = LecturerService.find_by_dni(dni)
                    if user is not None:
                        self.add_error('dni', _("There cannot be two users with the same ID number"))

        return self.cleaned_data


class SubjectEditForm(forms.Form):
    TIPO_ASIGNATURA = (
        ('FB', _('Basic formation')),
        ('OB', _('Compulsory')),
        ('OP', _('Optional')),
        ('TFG', _('Final degree thesis')),

    )

    DURACION = (
        ('A', _('Annual')),
        ('C', _('Quarterly')),
    )

    name = forms.CharField(
        label='name',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    course = forms.DecimalField(
        label='course',
        required=True,
        min_value=1,
        max_value=5,
        decimal_places=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '1',
                'max': '5',
            }
        )
    )

    code = forms.DecimalField(
        label='code',
        required=True,
        max_digits=254,
        min_value=0,
        decimal_places=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '0',
                'data-maxlength': '254',
            }
        )
    )

    quarter = forms.DecimalField(
        label='quarter',
        required=True,
        min_value=1,
        max_value=2,
        decimal_places=0,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '1',
                'max': '2',
            }
        )
    )

    credits = forms.DecimalField(
        label='credits',
        required=True,
        min_value=1,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'min': '1',
            }
        )
    )

    web = forms.URLField(
        label='web',
        required=False,
        max_length=254,
        widget=forms.URLInput(
            attrs={
                'class': 'form-control',
                'maxlength': '254',
            }
        )
    )

    duration = forms.ChoiceField(
        required=True,
        choices=DURACION,
        widget=forms.Select(
            attrs={
                'required': 'required',
            }
        )
    )

    type = forms.ChoiceField(
        required=True,
        choices=TIPO_ASIGNATURA,
        widget=forms.Select(
            attrs={
                'required': 'required',
            }
        )
    )

    departament = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        required=True,
        widget=forms.Select(
            attrs={
                'required': 'required',
            }
        )
    )

    def clean(self):
        code = self.cleaned_data.get('code')
        if code is not None:
            subject = SubjectService.find_by_code(code)
            if subject is not None:
                self.add_error('code', _("There cannot be two certifications with the same code"))

        return self.cleaned_data


class SubjectLinkEditForm(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput)

    certifications = forms.ModelMultipleChoiceField(
        queryset=Titulacion.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(
            attrs={

            }
        )
    )


class AddressForm(forms.Form):
    address = forms.CharField(label=_('Address'), required=True,
                              widget=forms.TextInput(attrs={'required': 'required', 'class': 'form-control'}))

    province = forms.CharField(label=_('Province'), required=True,
                               widget=forms.TextInput(attrs={'required': 'required', 'class': 'form-control'}))

    location = forms.CharField(label=_('Location'), required=True,
                               widget=forms.TextInput(attrs={'required': 'required', 'class': 'form-control'}))

    postal_code = forms.CharField(label=_('Postal code'), required=True,
                                  widget=forms.TextInput(
                                      attrs={'required': 'required', 'class': 'form-control', 'pattern': '[0-9]{5}',
                                             'title': _('Five digits')}))

    country = forms.CharField(label=_('Country'), required=True,
                              widget=forms.TextInput(attrs={'required': 'required', 'class': 'form-control'}))


class StudentProfileForm(forms.Form):
    global id_number_pattern
    id_number_pattern = '[0-9]{8}[a-zA-Z]{1}'

    student_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    photo = forms.ImageField(
        label=_('Photo'),
        required=False,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }
        ),
    )

    name = forms.CharField(label=_('Name'), required=True, max_length=30,
                           widget=forms.TextInput(
                               attrs={'required': 'required', 'class': 'form-control', 'maxlength': '30'}))

    surname = forms.CharField(label=_('Surname'), required=True, max_length=30,
                              widget=forms.TextInput(
                                  attrs={'required': 'required', 'class': 'form-control', 'maxlength': '30'}))

    email = forms.EmailField(label=_('Email'), required=True,
                             widget=forms.EmailInput(
                                 attrs={'required': 'required', 'class': 'form-control'}))

    id_number = forms.CharField(label=_('ID number'), required=True, widget=forms.TextInput(
        attrs={'required': 'required', 'class': 'form-control', 'pattern': id_number_pattern,
               'title': _('Not a valid ID number'), 'placeholder': _('Your ID number.')}))

    birth_date = forms.DateField(label=_('Birth date'),
                                 widget=forms.DateInput(attrs={'class': 'form-control', 'required': 'required'}),
                                 required=True)

    phone1 = forms.CharField(label=_('Telephone'), required=True,
                             widget=forms.TextInput(
                                 attrs={'required': 'required', 'class': 'form-control', 'pattern': '[0-9]{9}'}))

    phone2 = forms.CharField(label=_('Mobile phone'), required=True,
                             widget=forms.TextInput(
                                 attrs={'required': 'required', 'class': 'form-control', 'pattern': '[0-9]{9}'}))

    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id')
        super(StudentProfileForm, self).__init__(*args, **kwargs)
        self.fields['student_id'].initial = student_id

    def clean(self):
        student_id = self.fields['student_id'].initial
        date = self.cleaned_data['birth_date']
        id_number = self.cleaned_data['id_number']

        if re.match(id_number_pattern, id_number):
            if User.objects.filter(alumno__dni=id_number).exclude(pk=student_id).exists() or User.objects.filter(
                    profesor__dni=id_number).exclude(pk=student_id).exists():
                self.add_error('id_number', _("This ID number is already in use"))
        else:
            self.add_error('id_number', _("Not a valid ID number"))

        if date >= datetime.date.today():
            self.add_error('birth_date', _("You must select a date in the past."))

        if self.cleaned_data.get('photo'):
            content_types = ['image/png', 'image/jpg', 'image/jpeg']
            if self.cleaned_data.get('photo').content_type in content_types:
                if self.cleaned_data.get('photo').size > 512 * 1024:
                    self.add_error('photo', _("Image file too large. Max upload size is 512kb"))
            else:
                self.add_error('photo', _("Not a valid file. Only PNG, JPG and JPEG are supported"))

        return self.cleaned_data


class TutorialForm(forms.Form):
    WEEK_DAYS = (
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
    )

    # HOUR_CHOICES = ((
    #     '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30',
    #     '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
    #     '20:00', '20:30', '21:00', '21:30'))

    HOUR_CHOICES = (
        ('08:00', '08:00'), ('08:30', '08:30'), ('09:00', '09:00'), ('09:30', '09:30'), ('10:00', '10:00'),
        ('10:30', '10:30'), ('11:00', '11:00'), ('11:30', '11:30'), ('12:00', '12:00'), ('12:30', '12:30'),
        ('13:00', '13:00'), ('13:30', '13:30'), ('14:00', '14:00'), ('14:30', '14:30'), ('15:00', '15:00'),
        ('15:30', '15:30'), ('16:00', '16:00'), ('16:30', '16:30'), ('17:00', '17:00'), ('17:30', '17:30'),
        ('18:00', '18:00'), ('18:30', '18:30'), ('19:00', '19:00'), ('19:30', '19:30'), ('20:00', '20:00'),
        ('20:30', '20:30'), ('21:00', '21:00'), ('21:30', '21:30')
    )

    tutorial_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    # Lecturer id -> necessary for date validation (won't be rendered in HTML)
    lecturer_id = forms.IntegerField(label=_('Date range'), required=False, widget=forms.HiddenInput())

    start_hour = forms.TimeField(label=_('From'), required=True,
                                 widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'},
                                                     choices=HOUR_CHOICES))

    finish_hour = forms.TimeField(label=_('To'), required=True,
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': 'required'},
                                                      choices=HOUR_CHOICES))

    day = forms.IntegerField(label=_('Day'), required=True, widget=forms.Select(choices=WEEK_DAYS,
                                                                                attrs={'class': 'form-control',
                                                                                       'required': 'required'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(TutorialForm, self).__init__(*args, **kwargs)
        self.fields['lecturer_id'].initial = lecturer_id

    def clean(self):
        start = self.cleaned_data['start_hour']
        finish = self.cleaned_data['finish_hour']

        if start >= finish:
            self.add_error('start_hour', _('The start hour must be before the end hour.'))

        # Check date conflicts
        lecturer = Profesor.objects.get(id=self.fields['lecturer_id'].initial)

        same_day_tutorials = Tutoria.objects.exclude(id=self.cleaned_data['tutorial_id']).filter(
            dia=self.cleaned_data['day'], profesor=lecturer)
        for db_tutorial in same_day_tutorials:
            if not (finish <= db_tutorial.horainicio or start >= db_tutorial.horafin):
                # Conflict
                self.add_error('lecturer_id', _('There is a conflict between new date and the existing ones.'))
                break

        return self.cleaned_data


class DenyRequestForm(forms.Form):
    lecturer_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    request_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
    motivation = forms.CharField(label=_('Motivation'), required=True,
                                 widget=forms.Textarea(
                                     attrs={'class': 'form-control textarea-no-resize', 'required': 'required',
                                            'rows': '4', 'maxlength': '255'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(DenyRequestForm, self).__init__(*args, **kwargs)
        self.fields['lecturer_id'].initial = lecturer_id

    def clean(self):
        cleaned_data = super(DenyRequestForm, self).clean()

        lecturer = Profesor.objects.get(id=cleaned_data.get('lecturer_id'))
        tutorial_request = Peticioncita.objects.get(idcita=cleaned_data.get('request_id'))

        assert lecturer == tutorial_request.profesor

        form_motivation = cleaned_data.get('motivation')
        if form_motivation:
            if form_motivation.isspace() or '' == form_motivation:
                self.add_error('motivation', _('You have to enter a reason to reject a tutorial request.'))

        return self.cleaned_data


class UserLinkSubjectForm(forms.Form):
    subject_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput()
    )

    lecturer_id = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput()
    )

    position = forms.CharField(
        label='position',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
            }
        )
    )

    lecturer = forms.CharField(
        label='lecturer',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
                'readonly': 'readonly',
            }
        )
    )

    def clean(self):
        position = self.cleaned_data.get('position')
        lecturer_id = self.cleaned_data.get('lecturer_id')
        subject_id = self.cleaned_data.get('subject_id')
        if position is not None and lecturer_id is not None and subject_id is not None:

            try:
                Imparteasignatura.objects.get(asignatura__id=subject_id, profesor__id=lecturer_id)
                self.add_error('position', _("The lecturer is already linked to this subject"))
            except Imparteasignatura.DoesNotExist:
                pass

        return self.cleaned_data


class FileUploadForm(forms.Form):
    file_upload = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'accept': 'text/xml, text/csv',
                'required': 'required',
            }
        )

    )

    def clean(self):
        if self.cleaned_data.get('file_upload'):
            content_types = ['text/xml', 'text/csv']
            if self.cleaned_data.get('file_upload').content_type in content_types:
                if self.cleaned_data.get('file_upload').size > 512 * 1024:
                    self.add_error('file_upload', _("File file too large ( > 512kb )"))
            else:
                self.add_error('file_upload', _("Not valid file type. Only XML and CSV are supported"))

        return self.cleaned_data


class RemarkForm(forms.Form):
    lecturer_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    student_id = forms.IntegerField(required=True, widget=forms.HiddenInput())

    subject = forms.ModelChoiceField(label=_('Subject'), queryset=None, required=True,
                                     empty_label=_('Select a subject'),
                                     widget=forms.Select(
                                         attrs={
                                             'required': 'required',
                                             'class': 'form-control'
                                         }
                                     ))

    text = forms.CharField(label=_('Text'), required=True, widget=forms.Textarea(
        attrs={'class': 'form-control textarea-no-resize', 'required': 'required',
               'rows': '4', 'maxlength': '255'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(RemarkForm, self).__init__(*args, **kwargs)
        self.fields['lecturer_id'].initial = lecturer_id
        self.fields['subject'].queryset = SubjectService.get_lecturer_subjects(lecturer_id)


class PasswordForm(forms.Form):
    password = forms.CharField(
        required=True,
        label=_('New password'),
        max_length=31,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '31',
            }
        )
    )

    password_repeat = forms.CharField(
        label=_('Repeat new password'),
        required=True,
        max_length=31,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '32',
                'data-match': '#id_password',
                'data-match-error': _("Password mismatch")
            }
        )
    )

    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        new_password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_repeat')

        if new_password != password_confirmation:
            self.add_error('password_repeat', _('Password mismatch'))

        else:
            if new_password.isspace():
                self.add_error('password', _('Empty password'))


class LecturerProfileForm(forms.Form):
    name = forms.CharField(required=True, label=_('First name'), widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlenght': '29', 'required': 'required'}))

    surname = forms.CharField(required=True, label=_('Last name'), widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlenght': '29', 'required': 'required'}))

    category = forms.CharField(required=False, label=_('Category'),
                               widget=forms.TextInput(attrs={'class': 'form-control', 'maxlenght': '254'}))

    phone = forms.CharField(required=False, label=_('Telephone'),
                            widget=forms.TextInput(attrs={'class': 'form-control', 'maxlenght': '9'}))

    office = forms.CharField(required=False, label=_('Office'),
                             widget=forms.TextInput(attrs={'class': 'form-control', 'maxlenght': '10'}))

    web = forms.URLField(required=False, label=_('Web'),
                         widget=forms.URLInput(attrs={'class': 'form-control', 'maxlenght': '10'}))

    email = forms.EmailField(required=False, label=_('Email'),
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'maxlenght': '254'}))


class NewForm(forms.Form):
    new_id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    subject = forms.ModelChoiceField(label=_('Subject'), queryset=None, required=True,
                                     empty_label=_('Select a subject'),
                                     widget=forms.Select(
                                         attrs={
                                             'required': 'required',
                                             'class': 'form-control'
                                         }
                                     ))

    title = forms.CharField(required=True, label=_('Title'), widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlenght': '99', 'required': 'required'}))

    body = forms.CharField(required=True, label=_('Body'), widget=forms.Textarea(
        attrs={'class': 'form-control textarea-no-resize', 'required': 'required',
               'rows': '4', 'maxlength': '255'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(NewForm, self).__init__(*args, **kwargs)
        self.fields['subject'].queryset = SubjectService.get_lecturer_subjects(lecturer_id)


class FileUploadSubjectForm(forms.Form):
    file_upload = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'accept': 'text/xml, text/csv',
            }
        )

    )

    certifications = forms.ModelMultipleChoiceField(
        queryset=Titulacion.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )

    def clean(self):
        if self.cleaned_data.get('file_upload'):
            content_types = ['text/xml', 'text/csv']
            if self.cleaned_data.get('file_upload').content_type in content_types:
                if self.cleaned_data.get('file_upload').size > 512 * 1024:
                    self.add_error('file_upload', _("File file too large ( > 512kb )"))
            else:
                self.add_error('file_upload', _("Not valid file type. Only XML and CSV are supported"))

        return self.cleaned_data


class FileUploadSubjectLinkForm(forms.Form):
    subject = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput()
    )

    file_upload = forms.FileField(
        required=True,
        widget=forms.FileInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'accept': 'text/xml, text/csv',
            }
        )

    )

    subject_name = forms.CharField(
        label='lecturer',
        required=True,
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'required': 'required',
                'maxlength': '254',
                'readonly': 'readonly',
            }
        )
    )

    def clean(self):
        if self.cleaned_data.get('file_upload'):
            content_types = ['text/xml', 'text/csv']
            if self.cleaned_data.get('file_upload').content_type in content_types:
                if self.cleaned_data.get('file_upload').size > 512 * 1024:
                    self.add_error('file_upload', _("File file too large ( > 512kb )"))
            else:
                self.add_error('file_upload', _("Not valid file type. Only XML and CSV are supported"))

        return self.cleaned_data


class RejectAcceptedTutorialsForm(forms.Form):
    tutorial_requests = forms.ModelMultipleChoiceField(required=True, label=_('Requests to cancel'), queryset=None,
                                                       widget=forms.SelectMultiple(
                                                           attrs={'required': 'required', 'class': 'form-control'}))

    motivation = forms.CharField(label=_('Motivation'), required=True, widget=forms.Textarea(
        attrs={'class': 'form-control textarea-no-resize', 'required': 'required', 'rows': '4', 'maxlength': '254'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(RejectAcceptedTutorialsForm, self).__init__(*args, **kwargs)
        self.fields['tutorial_requests'].queryset = PeticionCitaService.lecturer_requests(lecturer_id, 'AC')


class LecturerStudentFilterForm(forms.Form):
    subject = forms.ModelChoiceField(required=False, label=_('Filter'), queryset=None, empty_label=_('All subjects'),
                                     widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        lecturer_id = kwargs.pop('lecturer_id')
        super(LecturerStudentFilterForm, self).__init__(*args, **kwargs)
        self.fields['subject'].queryset = SubjectService.get_lecturer_subjects(lecturer_id)


class TutorialRequestForm(forms.Form):
    lecturer = forms.IntegerField(label=_('Lecturer'), required=True, widget=forms.HiddenInput())

    date = forms.DateTimeField(label=_('Date'), required=True, widget=forms.HiddenInput())

    motivation = forms.CharField(label=_('Motivation'), required=True,
                                 widget=forms.Textarea(
                                     attrs={'class': 'form-control textarea-no-resize', 'required': 'required',
                                            'rows': '4', 'maxlength': '254'}))


class AutoAsignTutorialForm(forms.Form):
    date = forms.DateTimeField(label=_('Date'), required=True, widget=forms.HiddenInput())

    student = forms.ModelChoiceField(queryset=Alumno.objects.all(), required=True,
                                     empty_label=_('Type to search a student'),
                                     widget=forms.Select(
                                         attrs={'class': 'chosen-select', 'required': 'required'}))

    motivation = forms.CharField(label=_('Motivation'), required=True,
                                 widget=forms.Textarea(
                                     attrs={'class': 'form-control textarea-no-resize', 'required': 'required',
                                            'rows': '4', 'maxlength': '254'}))


class ValidatingPasswordChangeForm(PasswordChangeForm):
    MIN_LENGTH = 6

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        # At least MIN_LENGTH long
        if len(password1) < self.MIN_LENGTH:
            raise forms.ValidationError(_("The new password must be at least %d characters long.") % self.MIN_LENGTH)

        return password1
