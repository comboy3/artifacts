from django.shortcuts import render
from django.http import HttpResponse
from . import service

def index(request):
    return HttpResponse("Hello, world")

# POST通信
def doPost(request):
    service.reply_to_line(request.json)
    return '', 200, {}    