# -*- coding: utf-8 -*-
import requests
import json

class LineReplyMessage:
    """ 返信メッセージをJSONデータに編集するクラス """
    # トークン
    ACCESS_TOKEN = "tyl9iMxaFfz/V3/JH8/V3qVmdJFSMV1HiyD09BNkWu7LJfhQ6u8YxtC8S5KKsd5gPrijBAptKDcCbrUaS+jBS3TCtU6moPNocFfJODAyf6LXeA2o55knBUZ03uEqKJnjzyZV7ET6K0Dj2OkTFe4EkgdB04t89/1O/w1cDnyilFU="
    REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply' 

    def make_text_response(text):
        """ 送信テキスト """
        return {
            'type': 'text',
            'text': text
        }

    def send_reply(reply_token, messages):
        """ 送信 """
        payload = {
            'replyToken': reply_token,
            'messages': messages
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {}'.format(LineReplyMessage.ACCESS_TOKEN)
        }

        req = requests.post(
            LineReplyMessage.REPLY_ENDPOINT,
            data=json.dumps(payload),
            headers=headers)

        return req
