from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
# from . import service

#トークン
AccessToken = "8GyCMQe6p9BVNXNwvl9ysE2BInxVnvXedqCqiBfUWbkqW1k+/JyjuNMUkP5VcI9YveuboZiu7dzVUJzs/8IIdbeCAEdPkAQQOHpjpuudZwYchZOw4cJWfU5E5xBvmgP3TPMDgzqJzndpm4ERjpFNEQdB04t89/1O/w1cDnyilFU="

def index(request):
    return HttpResponse("Hello, world")

# POST通信
def doPost(request):

    if request.method == "POST":
        params = json.loads(request.body.decode())
        print(params)

    for event in params['events']:
        responses = []

        replyToken = event['replyToken']
        type = event['type']
        
        if type == 'message':
            message = event['message']
            if message['type'] == 'text':
                # そのままオウム返し
                responses.append(LineReplyMessage.make_text_response(message['text']))
            else:
                # テキスト以外のメッセージにはてへぺろしておく
                responses.append(LineReplyMessage.make_text_response('てへぺろ'))

        # 返信する
        req = LineReplyMessage.send_reply(replyToken, responses)
        
    return HttpResponse(req)    

class LineReplyMessage:
    ReplyEndpoint = 'https://api.line.me/v2/bot/message/reply'

    @staticmethod
    def make_text_response(text):
        return {
            'type': 'text',
            'text': text
        }

    @staticmethod
    def send_reply(replyToken, messages):
        payload = {
            'replyToken': replyToken,
            'messages': messages
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(AccessToken)
        }

        req = requests.post(
            LineReplyMessage.ReplyEndpoint,
            data=json.dumps(payload),
            headers=headers)

        return req
    