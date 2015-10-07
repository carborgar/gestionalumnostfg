from django.contrib.auth.decorators import permission_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from principal.forms import DepartmentEditForm, FileUploadForm
from principal.services import DepartmentService
from django.utils.translation import ugettext as _
from django.contrib import messages
import xmltodict
import csv


@permission_required('principal.administrator')
def edit_department(request, department_id):

    data_form = {}
    data_template = {}

    if request.POST:
        form = DepartmentEditForm(request.POST)

        try:

            if department_id:
                assert department_id == form.cleaned_data['id']

        except AssertionError:
            messages.error(request, _("Action failed, try again!"))
            return HttpResponseRedirect('/admin/department/lis')

        if form.is_valid():
            department = DepartmentService.reconstruct_and_save(form)
            messages.success(request, _("Action completed successfully"))
            redirect = '/admin/department/details/' + str(department.id)
            return HttpResponseRedirect(redirect)
    else:

        if department_id:
            department = DepartmentService.find_one(department_id)
            data_form = DepartmentService.get_form_data(department)

        form = DepartmentEditForm(initial=data_form)

    if department_id:
        data_template['create'] = False
        data_template['cancel'] = '/admin/department/details/' + str(department_id)
    else:
        data_template['create'] = True

    data_template['form'] = form
    data_template['action'] = '/admin/department/edit/'
    template_name = 'department/edit.html'
    return render_to_response(template_name, data_template, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def list_departments(request):

    departments = DepartmentService.find_all()
    template_name = 'department/list.html'
    template_data = {"departments": departments}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def search(request):

    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''

    departments = DepartmentService.search(search_text)
    template_name = 'department/ajax_search.html'
    template_data = {'departments': departments}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def details_department(request, department_id):

    department = DepartmentService.find_one(department_id)
    subjects = department.asignatura_set.all()
    template_name = 'department/details.html'
    template_data = {'department': department, 'subjects': subjects}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def import_department(request):

    import_errors_create = []
    department_create = []
    template_name = 'department/import_department.html'
    template_data = {}

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file_name = form.cleaned_data['file_upload']
            data = file_name.read()
            file_name.close()

            try:
                if form.cleaned_data['file_upload'].content_type == "text/xml":
                    data = xmltodict.parse(data)

                    if data['departamentos']:

                        if not isinstance(data['departamentos']['departamento'], list):
                            # 1 value
                            department_data = data['departamentos']['departamento']
                            data_form = DepartmentService.get_form_data_xml(department_data)
                            create_department_file(data_form, import_errors_create, department_create)
                        else:

                            for department_data in data['departamentos']['departamento']:
                                data_form = DepartmentService.get_form_data_xml(department_data)
                                create_department_file(data_form, import_errors_create, department_create)
                else:
                    # File CSV
                    for department in csv.reader(data.splitlines()):
                        data_form = DepartmentService.get_form_data_csv(department)
                        create_department_file(data_form, import_errors_create, department_create)

                if import_errors_create:
                    message = _('Action completed successfully')
                    messages.warning(request, message)
                    template_data['import_errors_create'] = import_errors_create
                else:
                    message = _('Action completed successfully')
                    messages.success(request, message)

                form = FileUploadForm()

            except KeyError as e:
                message = _("The file structure is wrong. It needs a label called:: " + e.message)
                form.add_error('file_upload', message)
                DepartmentService.rollback(department_create)
            except AttributeError:
                message = _("Please, check the attributes of the subjects")
                form.add_error('file_upload', message)
                DepartmentService.rollback(department_create)
            except TypeError:
                message = _("Please, check the xml syntax and data values")
                form.add_error('file_upload', message)
                DepartmentService.rollback(department_create)
            except Exception:
                message = _("Please, check the file")
                form.add_error('file_upload', message)
                DepartmentService.rollback(department_create)
    else:
        form = FileUploadForm()

    template_data['form'] = form
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


def create_department_file(data_form, import_errors_create, department_create):

    form_department = DepartmentEditForm(data=data_form)

    if form_department.is_valid():
        department = DepartmentService.reconstruct_and_save(form_department)
        department_create.append(department)
    else:
        name = form_department.data['name']
        code = form_department.data['code']
        import_errors_create.append(name + " (" + code + ")")
