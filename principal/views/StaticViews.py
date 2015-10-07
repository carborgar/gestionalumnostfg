__author__ = 'Carlos'

from django.http import HttpResponseServerError, HttpResponseNotFound
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required


def error_404(request):
    template = get_template('404.html')
    return HttpResponseNotFound(template.render(RequestContext(request)))


def error_500(request):
    template = get_template('500.html')
    return HttpResponseServerError(template.render(RequestContext(request)))


@login_required
def home(request):
    return render_to_response('home.html', {}, context_instance=RequestContext(request))


def cookies_policy(request):
    return render_to_response('cookies.html', {}, context_instance=RequestContext(request))