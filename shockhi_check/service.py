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

                # 月末日の取得
                now_date = datetime.datetime.now()
                now_year = now_date.year
                now_month = now_date.month

                start_date = datetime.date(now_year, now_month, 1)
                end_date = datetime.date(now_year, now_month + 1, 1) - datetime.timedelta(days=1)
                end_day = end_date.strftime("%d")

                if reply_text != "リセット":
                    # 食費の登録
                    s = Shokuhi(user_id=reply_user_id, money=reply_text)
                    s.save()


                    # 中央値の算出
                    money_list = Shokuhi.objects.filter(user_id=reply_user_id, create_date__range=[start_date, end_date]).values("money")
                    df_money_list = read_frame(money_list)
                    total = df_money_list["money"].sum()
                    median = df_money_list["money"].median()
                    month_money = int(median) * int(end_day)

                    today_money_list = money_list.filter(create_date__date=now_date)
                    df_today_money_list = read_frame(today_money_list)
                    today_total = df_today_money_list["money"].sum()

                    # 中央値を返す
                    # head = "本日の食費現在：{0:,}円".format(today_total)
                    text = "{0}月の食費を教えるよ\n今日：{1:,}円\n今月：{2:,}円\n予想：{3:,}円".format(now_month, today_total, total, month_money) 
                else:
                    d = Shokuhi.objects.filter(user_id=reply_user_id, create_date__range=[start_date, end_date])
                    d.delete()
                    text = "{0}月分をリセットしました".format(now_month)

                responses.append(LineReplyMessage.make_text_response(text))
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
