__author__ = 'Carlos'

import json as json_lib

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from principal.services import LecturerService


@login_required
def list_lecturers(request, subject_id):
    lecturers = LecturerService.lecturers_of_subject(subject_id)

    return render_to_response('lecturer/list.html', {'lecturers': lecturers},
                              context_instance=RequestContext(request))


def get_lecturers_json(request, subject_id):
    lecturers = LecturerService.lecturers_of_subject(subject_id)
    json = json_lib.dumps(
        [{'id': lecturer.id, 'name': lecturer.first_name + ' ' + lecturer.last_name} for lecturer in lecturers])

    return JsonResponse(json, safe=False)
