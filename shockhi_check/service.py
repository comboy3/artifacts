# -*- coding: utf-8 -*-
import requests
import json
import logging
from shockhi_check.models import Token, Shokuhi

logger = logging.getLogger()

#トークン
AccessToken = "8GyCMQe6p9BVNXNwvl9ysE2BInxVnvXedqCqiBfUWbkqW1k+/JyjuNMUkP5VcI9YveuboZiu7dzVUJzs/8IIdbeCAEdPkAQQOHpjpuudZwYchZOw4cJWfU5E5xBvmgP3TPMDgzqJzndpm4ERjpFNEQdB04t89/1O/w1cDnyilFU="

def reply_to_line(params):

    a = Token.get_deferred_fields
    logger.info(a)

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
        
        userId = event["source"].userId

        t = Token(token=userId)
        t.save()
        # s = Shokuhi(token=replyToken, money=500)
        # s.save()

    return req

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