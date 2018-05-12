from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
from . import service

#トークン
AccessToken = "8GyCMQe6p9BVNXNwvl9ysE2BInxVnvXedqCqiBfUWbkqW1k+/JyjuNMUkP5VcI9YveuboZiu7dzVUJzs/8IIdbeCAEdPkAQQOHpjpuudZwYchZOw4cJWfU5E5xBvmgP3TPMDgzqJzndpm4ERjpFNEQdB04t89/1O/w1cDnyilFU="

def index(request):
    return HttpResponse("Hello, world")

# POST通信
def doPost(request):

    if request.method == "POST":
        params = json.loads(request.body.decode())
        print(params)

        req = service.reply_to_line(params)

    return HttpResponse(req)    
