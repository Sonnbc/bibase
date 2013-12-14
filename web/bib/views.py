import json

from django.core.context_processors import csrf
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from controller import Controller, bib_string
import util

def index(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('bib/index.html', c)

#TODO: remove exemption
@csrf_exempt
def getbib(request):
    keys = dict(request.POST.iterlists()).get('keys[]')

    print dict(request.POST.iterlists())

    if not keys:
        return HttpResponse("", content_type='application/json')

    con = Controller()

    result = {}
    for key in keys:
        result[key] = con.get(key)
        
    return HttpResponse(json.dumps(result), content_type='application/json')
