# -*- coding: utf-8 -*-
import json
import logging
import datetime 

from django_pandas.io import read_frame
import requests

from shockhi_check.models import Shokuhi, User

logger = logging.getLogger()

#トークン
access_token = "tyl9iMxaFfz/V3/JH8/V3qVmdJFSMV1HiyD09BNkWu7LJfhQ6u8YxtC8S5KKsd5gPrijBAptKDcCbrUaS+jBS3TCtU6moPNocFfJODAyf6LXeA2o55knBUZ03uEqKJnjzyZV7ET6K0Dj2OkTFe4EkgdB04t89/1O/w1cDnyilFU="

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
 
                # 月末日の取得
                now_date = datetime.datetime.now()
                str_now_date = now_date.strftime('%Y-%m-%d')
                now_year = now_date.year
                now_month = now_date.month
                now_day = now_date.day

                # 時間帯の判定
                if now_date.hour in range(3,12):
                    now_timezone = "朝"
                elif now_date.hour in range(12,17):
                    now_timezone = "昼"
                else:
                    now_timezone = "夜"

                start_date = datetime.date(now_year, now_month, 1)
                end_date = datetime.date(now_year, now_month + 1, 1) - datetime.timedelta(days=1)
                end_day = end_date.strftime("%d")
                
                message_text = message['text'].strip()
                reply_texts = message_text.split(" ")
                reply_text = reply_texts[0].replace("円","")
                reply_eat = None
                reply_date = None
                reply_time_zone = now_timezone
                
                if len(reply_texts) >= 2:
                    try:
                        for reply_tmp in reply_texts[1:]: 
                            reply_tmps = reply_tmp.split("/")
                            if len(reply_tmps) == 2:
                                reply_date = datetime.date(now_year, int(reply_tmps[0]), int(reply_tmps[1]))
                            else:
                                reply_eat = reply_tmp
                    except Exception as e:
                        logger.error("食べ物または日付の取得で失敗しました。",e)
                        responses.append(LineReplyMessage.make_text_response('入力まちがえてない？'))
                        req = LineReplyMessage.send_reply(reply_token, responses)
                        return req

                if reply_date is None:
                    reply_date = datetime.date(now_year, now_month, now_day)  
                else:
                    reply_time_zone = None            

                if reply_text == "今月をリセット":
                    d = Shokuhi.objects.filter(user_id=reply_user_id, date__range=[start_date, end_date])
                    d.delete()
                    text = "今月をリセットしました"
                elif reply_text == "今日をリセット":
                    d = Shokuhi.objects.filter(user_id=reply_user_id, date=str_now_date)
                    d.delete()
                    text = "今日をリセットしました"

                elif reply_text.isdecimal() or reply_text[0:1] == "-" or reply_text == "予測":
                    
                    try: 
                        if reply_text != "予測":
                            # 食費の登録
                            s = Shokuhi(user_id=reply_user_id, money=reply_text, eat=reply_eat, date=reply_date, time_zone=reply_time_zone)
                            s.save()

                        # 食費の取得
                        money_list = Shokuhi.objects.filter(user_id=reply_user_id, date__range=[start_date, end_date]).values("money")
                        df_money_list = read_frame(money_list)
                        
                        if reply_text != "予測":
                            total = df_money_list["money"].sum()
                            today_money_list = money_list.filter(date=str_now_date)
                            df_today_money_list = read_frame(today_money_list)
                            today_total = df_today_money_list["money"].sum()

                            text = "{0}月{1}日（{4}）\n食費を教えるよ\n本日：{2:,}円\n今月：{3:,}円".format(now_month, now_day, today_total, total, now_timezone) 
                        else:                 
                            median = df_money_list["money"].median()
                            month_money = int(median) * int(end_day)
                    
                            text = "{0}月の食費の予測だよ\n予測：{1:,}円".format(now_month, month_money)                     
                    except Exception as e:
                        logger.error("エラーが発生しました。",e)
                elif reply_text == "コンコン" or reply_text == "こんこん":
                    text = "コンコンの食費を教えるよ\n本日：5兆円"
                else:
                    text = "「金額（数字）」or「今日（今月）をリセット」を入力してね"

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