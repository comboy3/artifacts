from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
from . import service

def index(request):
    return HttpResponse("Hello, world")

# POST通信
def doPost(request):

    if request.method == "POST":
        params = json.loads(request.body.decode())
        print(params)

        req = service.reply_to_line(params)

    return HttpResponse(req)    
