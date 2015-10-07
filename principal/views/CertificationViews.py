from django.contrib.auth.decorators import permission_required
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from principal.forms import CertificationEditForm
from principal.services import CertificationService
from django.utils.translation import ugettext as _
from django.contrib import messages


@permission_required('principal.administrator')
def create_certification(request):

    if request.POST:
        form = CertificationEditForm(request.POST)
        if form.is_valid():
            CertificationService.create_and_save(form)
            messages.success(request, _("Action completed successfully"))
            return HttpResponseRedirect("/admin/certification/list")
    else:
        data = {}
        form = CertificationEditForm(initial=data)

    template_name = 'certification/edit.html'
    template_data = {"form": form, "create": True}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def list_certifications(request):

    certifications = CertificationService.find_all()
    template_name = 'certification/list.html'
    template_data = {'certifications': certifications}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def search(request):

    if request.POST:
        search_text = request.POST['search_text']
    else:
        search_text = ''

    certifications = CertificationService.search(search_text)
    template_name = 'certification/ajax_search.html'
    template_data = {'certifications': certifications}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))


@permission_required('principal.administrator')
def delete_certification(request, certification_id):

    certification = CertificationService.find_one(certification_id)
    certification.delete()
    messages.success(request, _('Action completed successfully'))
    return HttpResponseRedirect('/admin/certification/list')


@permission_required('principal.administrator')
def details_certification(request, certification_id):

    certification = CertificationService.find_one(certification_id)
    subjects = certification.asignaturas.all()
    template_name = 'certification/details.html'
    template_data = {'certification': certification, 'subjects': subjects}
    return render_to_response(template_name, template_data, context_instance=RequestContext(request))
