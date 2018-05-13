# -*- coding: utf-8 -*-
import json
import logging
import datetime 

from django_pandas.io import read_frame
import requests

from shockhi_check.models import Shokuhi, User

logger = logging.getLogger()

#トークン
access_token = "8GyCMQe6p9BVNXNwvl9ysE2BInxVnvXedqCqiBfUWbkqW1k+/JyjuNMUkP5VcI9YveuboZiu7dzVUJzs/8IIdbeCAEdPkAQQOHpjpuudZwYchZOw4cJWfU5E5xBvmgP3TPMDgzqJzndpm4ERjpFNEQdB04t89/1O/w1cDnyilFU="

def reply_to_line(params):

    # params = {
    #     "events" : {
    #         "replyToken" : "test",
    #         "type" : "message",
    #         "source" : { 
    #             "userId" : "12345"
    #         },
    #         "message" : {
    #             "type" : "text",
    #             "text" : "500"
    #         }
    #     }
    # }

    for event in params['events']:
        responses = []

        reply_token = event['replyToken']
        type = event['type']

        source = event["source"]
        reply_user_id = source["userId"]
        logger.info(reply_user_id)

        # ユーザーIDの登録
        User.objects.get_or_create(user_id=reply_user_id)
        
        if type == 'message':
            message = event['message']
            if message['type'] == 'text':

                reply_text = message['text']

                # 食費の登録
                s = Shokuhi(user_id=reply_user_id, money=reply_text)
                s.save()

                # 月末日の取得
                now_year = datetime.datetime.now().year
                now_month = datetime.datetime.now().month

                end_date = datetime.date(now_year, now_month, 1) - datetime.timedelta(days=1)
                end_day = end_date.strftime("%d")

                # 中央値の算出
                money_list = Shokuhi.objects.filter(user_id=reply_user_id).values("money")
                df_money_list = read_frame(money_list)
                median = df_money_list.median()
                month_money = round(median) * int(end_day)
                

                # 中央値を返す
                responses.append(LineReplyMessage.make_text_response(month_money))
            else:
                # テキスト以外のメッセージにはてへぺろしておく
                responses.append(LineReplyMessage.make_text_response('てへぺろ'))

        # 返信する
        req = LineReplyMessage.send_reply(reply_token, responses)

    return req


class LineReplyMessage:
    """ 送信メッセージ """
    ReplyEndpoint = 'https://api.line.me/v2/bot/message/reply'

    @staticmethod
    def make_text_response(text):
        """ 送信テキスト """
        return {
            'type': 'text',
            'text': text
        }

    @staticmethod
    def send_reply(reply_token, messages):
        """ 送信 """
        payload = {
            'replyToken': reply_token,
            'messages': messages
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(access_token)
        }

        req = requests.post(
            LineReplyMessage.ReplyEndpoint,
            data=json.dumps(payload),
            headers=headers)
        
        return req
