from django.http import HttpResponse
from django.shortcuts import redirect


def index(request):
    return redirect('store:demo_cases')


def open_case(request, case_id):
    return HttpResponse(
        'This legacy case endpoint is disabled. Use the safe demo case flow.',
        status=410,
        content_type='text/plain; charset=utf-8',
    )