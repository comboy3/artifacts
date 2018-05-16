# -*- coding: utf-8 -*-
import json
import logging
import datetime 

from django_pandas.io import read_frame
import requests

from shockhi_check.models import Shokuhi, User

logger = logging.getLogger()

#トークン
access_token = "48klff7U3aeqw06WBsIOMNonRdMC9N8LenZ1LgQv15t7nO7FW/47je01dXebo+JJsJVN2CAnhZ7Se47kE1Ac+jZZpnPxBQm0nYSfpinQb7nrcQaJ+18xHoqRPUNauicV7Kwkk5iOziBDOXkV8WUvogdB04t89/1O/w1cDnyilFU="

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
                now_day = now_date.day

                start_date = datetime.date(now_year, now_month, 1)
                end_date = datetime.date(now_year, now_month + 1, 1) - datetime.timedelta(days=1)
                end_day = end_date.strftime("%d")

                if reply_text == "今月をリセット":
                    d = Shokuhi.objects.filter(user_id=reply_user_id, create_date__range=[start_date, end_date])
                    d.delete()
                    text = "今月をリセットしました"
                elif reply_text == "今日をリセット"
                    d = Shokuhi.objects.filter(user_id=reply_user_id, create_date__date=now_date)
                    d.delete()
                    text = "今日をリセットしました"

                elif type(reply_text) == "int" or reply_text == "予測":
                    
                    if reply_text != "予測"
                        # 食費の登録
                        s = Shokuhi(user_id=reply_user_id, money=reply_text)
                        s.save()

                    # 食費の取得
                    money_list = Shokuhi.objects.filter(user_id=reply_user_id, create_date__range=[start_date, end_date]).values("money")
                    if reply_text != "予測":
                        total = df_money_list["money"].sum()
                        today_money_list = money_list.filter(create_date__date=now_date)
                        df_today_money_list = read_frame(today_money_list)
                        today_total = df_today_money_list["money"].sum()

                        text = "{0}月{1}日の食費を教えるよ\n本日：{2:,}円\n今月：{3:,}円".format(now_month, now_day, today_total, total) 
                    else:                 
                        df_money_list = read_frame(money_list)
                        median = df_money_list["money"].median()
                        month_money = int(median) * int(end_day)
                  
                        text = "{0}月の食費の予測だよ\n予測：{1:,}円".format(now_month, month_money)                     
                else:
                    text = "「金額（数字）」\nor「今日（今月）をリセット」\nor「予測」を入力してね"

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


class PredictionMoney:
    """ 予測計算するクラス """
