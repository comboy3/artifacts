# -*- coding: utf-8 -*-
import datetime
import logging

from django_pandas.io import read_frame

from shockhi_check.make_message import LineReplyMessage
from shockhi_check.models import Shokuhi, User

from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger()

def reply_to_line(params):
    """ LINEに応答するメソッド """
    # 受け取ったJSONデータからテキストを取得する
    for event in params['events']:
        responses = []

        reply_token = event['replyToken']
        type = event['type']

        # ユーザIDを取得する
        source = event["source"]
        reply_user_id = source["userId"]
        logger.info(reply_user_id)

        # ユーザーIDの登録
        User.objects.get_or_create(user_id=reply_user_id)
        
        # テキストを取得する
        if type == 'message':
            message = event['message']
            # 取得したメッセージのタイプがテキストの場合
            if message['type'] == 'text':
 
                """ 日付の編集 """
                # 今日の日付を取得する
                now_date = datetime.datetime.now()
                # datetime型の日付を、Str型の日付に変換
                str_now_date = now_date.strftime('%Y-%m-%d')
                now_year = now_date.year
                now_month = now_date.month
                now_day = now_date.day
                # 月末日の取得
                start_date = datetime.date(now_year, now_month, 1)
                end_date = datetime.date(now_year, now_month + 1, 1) - datetime.timedelta(days=1)
                end_day = end_date.strftime("%d")

                # 時間帯の判定
                if now_date.hour in range(3,12):
                    now_timezone = "朝"
                elif now_date.hour in range(12,17):
                    now_timezone = "昼"
                else:
                    now_timezone = "夜"
                
                """ 受信したテキストを編集 """
                # テキストの両端のスペースを削除
                message_text = message['text'].strip()
                # 半角スペースごとにリストに分割（金額、食品名、日付）
                reply_texts = message_text.split(" ")
                # 金額についている"円"を削除
                reply_text = reply_texts[0].replace("円","")
                # 返信用の変数の初期化
                reply_eat = None
                reply_date = None
                reply_time_zone = now_timezone
                
                """　食品名または日付が付与されていた場合 """
                if len(reply_texts) >= 2:
                    # 食品名または日付の編集メソッドを呼び出す
                    reply_list = edit_text(reply_texts, now_year)
                    # 編集メソッドの結果を判定（正常:True)
                    if reply_list["result"]:
                        # 編集メソッドで取得した値を代入
                        reply_eat = reply_list["eat"]
                        reply_date = reply_list["date"]
                    else:
                        # エラーの場合、入力値の確認を促すメッセージを返信する
                        responses.append(LineReplyMessage.make_text_response('入力まちがえてない？'))
                        req = LineReplyMessage.send_reply(reply_token, responses)
                        return req
                    
                # 応答用の日付の変数がNone（null）の場合（日付が付与されていない場合）
                if reply_date is None:
                    # 登録用の日付の変数に、今日の日付を設定する
                    reply_date = datetime.date(now_year, now_month, now_day)  
                # 応答用の日付の変数に、日付が存在する場合（日付が付与されていた場合）
                else:
                    # 登録用の時間帯の変数に、None(null)を設定する　※特定できないため
                    reply_time_zone = None            

                """ メッセージで受けた処理を実行する """
                # 今月のリセット処理
                if reply_text == "今月をリセット":
                    # 食費テーブルにある、ユーザの月初めの日から月末日までデータをすべて削除する
                    d = Shokuhi.objects.filter(user_id=reply_user_id, date__range=[start_date, end_date])
                    d.delete()
                    text = "今月をリセットしました"
                # 今日のリセット処理
                elif reply_text == "今日をリセット":
                    # 食費テーブルにある、ユーザの今日のデータをすべて削除する
                    d = Shokuhi.objects.filter(user_id=reply_user_id, date=str_now_date)
                    d.delete()
                    text = "今日をリセットしました"

                # テキストが数字か、"予測"の場合、
                elif reply_text.isdecimal() or reply_text[0:1] == "-" or reply_text == "予測":
                    
                    try: 
                        # テキストが"予測"と０以外の場合（数字）
                        if reply_text != "予測" and reply_text != "0":
                            # 食費の登録（ユーザID、金額、食品名、日付、時間帯）
                            s = Shokuhi(user_id=reply_user_id, money=reply_text, eat=reply_eat, date=reply_date, time_zone=reply_time_zone)
                            s.save()

                        # 1ヵ月間の食費の取得（金額）
                        money_list = Shokuhi.objects.filter(user_id=reply_user_id, date__range=[start_date, end_date])
                        # テーブルから取得したクエリセットを、データフレームに変換
                        df_money_list = read_frame(money_list)

                        # 1ヵ月間の食費の合計
                        total = df_money_list["money"].sum()
                        # 1か月間で入力した日数           
                        date_count = df_money_list["date"].nunique()

                        # テキストが予測以外の場合（数字）                        
                        if reply_text != "予測":
                            # 1か月間の食費のクエリセットから、本日の食費を取得
                            today_money_list = money_list.filter(date=str_now_date)
                            df_today_money_list = read_frame(today_money_list)
                            # 本日の食費の合計
                            today_total = df_today_money_list["money"].sum()
                            # 文字列フォーマットで返信のテキストを編集する
                            text = "{0}月{1}日（{4}）\n食費を教えるよ\n本日：{2:,}円\n今月：{3:,}円\n入力日数：{5}日".format(now_month, now_day, today_total, total, now_timezone, date_count) 
                        # テキストが予測の場合（別の算出方法を検討中）
                        else:
                            # 1か月間の入力した食費の平均を算出                 
                            tmp_input_average = total / date_count
                            input_average = Decimal(tmp_input_average).quantize(Decimal('0'), rounding=ROUND_HALF_UP)
                            # 月末日 - 入力した日数
                            remaining_days = int(end_day) - date_count
                            # 平均値を1ヵ月間のあまってる日数で掛ける
                            remaining_money = input_average * remaining_days
                            # 予測の食費 
                            month_money = total + remaining_money
                            
                            text = "{0}月の食費の予測だよ\n1日当たり：{1:,}円\n予測：{2:,}円".format(now_month, input_average, round(month_money))                 
                    except Exception as e:
                        logger.error("エラーが発生しました。",e)
                # 隠しワード（特にいらない）
                elif reply_text == "コンコン" or reply_text == "こんこん":
                    text = "コンコンの食費を教えるよ\n本日：5兆円\n今月：5000兆円"
                # テキストが数字以外、特定の文字列以外の場合
                else:
                    text = "「金額（数字）」or「今日（今月）をリセット」or「予測」を入力してね"
                # 編集したテキストを返信用のJSONデータに追加する
                responses.append(LineReplyMessage.make_text_response(text))
            else:
                # テキスト以外のメッセージにはてへぺろしておく
                responses.append(LineReplyMessage.make_text_response('てへぺろ'))

        # 返信する
        req = LineReplyMessage.send_reply(reply_token, responses)

    return req

def edit_text(reply_texts, now_year):
    """　食品名または日付の編集メソッド """
    resut_list = {"result":True}
    try:
        # リストを1番目からスライスで取得
        for reply_tmp in reply_texts[1:]:
            # スラッシュをもとに文字列を分割 
            reply_tmps = reply_tmp.split("/")
            # スラッシュで分割された場合（日付の場合）
            if len(reply_tmps) == 2:
                # 登録用の日付の変数に、受信した日付を代入
                reply_date = datetime.date(now_year, int(reply_tmps[0]), int(reply_tmps[1]))
                resut_list.update({"date" : reply_date})
            # スラッシュで分割されない場合（食品名の場合）
            else:
                # 登録用の食品名の変数に、受信した食品名を代入
                reply_eat = reply_tmp
                resut_list.update({"eat":reply_eat})

        return resut_list
    # エラーになった場合
    except Exception as e:
        logger.error("食べ物または日付の取得で失敗しました。",e)
        resut_list["result"] = False
        return resut_list
