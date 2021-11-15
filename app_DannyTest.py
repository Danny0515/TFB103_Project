from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, AudioMessage, ImageSendMessage,
    ConfirmTemplate, TemplateSendMessage, MessageTemplateAction,
    StickerSendMessage, ButtonsTemplate)
import configparser
from app_accounting import *


app = Flask(__name__)

# LINE bot connection info
config = configparser.ConfigParser()
config.read('./config/config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# Get LINE bot message from user
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# Speech accounting function
@handler.add(MessageEvent, message=AudioMessage)
def accounting_main(event):
    # Create a directory to save image
    accounting_mkdir()
    user_id = event.source.user_id
    rawAudio = line_bot_api.get_message_content(event.message.id)

    # Convert .acc to .wav for GCP speech-to-text api
    newAudio = covert_audio(user_id, rawAudio)
    # Use GCP api speech-to-text
    rawSpeechText = call_gcp_speech_to_ext(newAudio)
    print(f'Speech Text = {rawSpeechText}')

    if check_budget(user_id):
        speechText = speech_text_clean(rawSpeechText)  # return -> ex: {'早餐': 100, '捷運': 70,}
        # Response user before insert data to mysql
        responseMsg = response_user(user_id, speechText)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(responseMsg))
        # Identify items from speechText,and insert data to mysql
        if responseMsg != '抱歉我沒聽清楚QQ，麻煩再說一次~\n謝謝':
            identify_items(user_id, speechText)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage('請先新增預算才能幫你算錢喔~\nex: 新增預算30000')
            )

@handler.add(MessageEvent, message=TextMessage)
def accounting_show_statistics(event):
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    # message_type = event.message.type
    text_content = event.message.text
    if text_content == '@語音記帳':
        accounting_button(event)
    elif text_content == '@計算中稍等一下喔~':
        foodCost, shopCost, liveCost, trafficCost, entCost, otherCost, totalCost \
            = accounting_statistics(user_id)
        budget, balance = query_budget(user_id)
        msg = f'你的預算為: {budget}\n' \
              f'目前已花費: {totalCost}\n' \
              f'目前餘額: {balance}\n' \
              f'餐飲: {foodCost}\n' \
              f'購物: {shopCost}\n' \
              f'住宿: {liveCost}\n' \
              f'交通: {trafficCost}\n' \
              f'娛樂: {entCost}\n' \
              f'其他: {otherCost}'
        image1Url, image2Url = get_image_url(user_id)
        print(f'name =  {user_name}\nid = {user_id}')
        print(f'message = \n{msg}\n{image1Url}\n{image2Url}')
        if totalCost < budget:
            line_bot_api.reply_message(
                event.reply_token, [
                    ImageSendMessage(original_content_url=image1Url,
                                     preview_image_url=image1Url),
                    ImageSendMessage(original_content_url=image2Url,
                                     preview_image_url=image2Url),
                    TextSendMessage(msg)])
        else:
            line_bot_api.reply_message(
                event.reply_token, [
                    ImageSendMessage(original_content_url=image1Url,
                                     preview_image_url=image1Url),
                    ImageSendMessage(original_content_url=image2Url,
                                     preview_image_url=image2Url),
                    TextSendMessage(msg),
                    TextSendMessage('超支了!! 錢錢掰掰'),
                    StickerSendMessage(package_id='1070', sticker_id='17871')])
    elif '@預算' == text_content:
        msg = edit_budget(user_id, text_content)
        line_bot_api.reply_message(event.reply_token,TextSendMessage(msg))
    elif text_content == '刪除花費':
        accounting_clean_check(event)
    elif '@確認刪除花費' in text_content:
        msg = clean_budget(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))

def accounting_button_2(event):
    welcome_msg = '你好~歡迎使用語音記帳功能\n' \
                  '1.初次使用請先新增預算\n' \
                  '輸入格式ex:「新增預算100000」\n' \
                  '2.直接對我說話開始記帳\n' \
                  '3.輸入「預算」可查看預算功能\n' \
                  '4.輸入「刪除花費」可清空紀錄'
    try:
        message = TemplateSendMessage(
            alt_text='記帳功能主頁',
            template=ConfirmTemplate(
                text='歡迎使用語音記帳\n初次使用請點選「開始使用」',
                actions=[
                    MessageTemplateAction(
                        label='開始使用',
                        text=welcome_msg
                    ),
                    MessageTemplateAction(
                        label='即時統計',
                        text='@計算中稍等一下喔~'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！請稍後再試'))

def accounting_button(event):
    welcome_msg = '你好~歡迎使用語音記帳功能\n' \
                  '1.初次使用請先新增預算\n' \
                  '輸入格式ex:「新增預算100000」\n' \
                  '2.直接對我說話開始記帳\n' \
                  '3.輸入「預算」可查看預算功能\n' \
                  '4.輸入「刪除花費」可清空紀錄'
    try:
        message = TemplateSendMessage(
            alt_text='按鈕樣板',
            template=ButtonsTemplate(
                thumbnail_image_url='https://i.imgur.com/4QfKuz1.png',
                title='歡迎使用語音記帳',
                text='請選擇：',
                actions=[
                    MessageTemplateAction(
                        label='開始使用',
                        text=welcome_msg
                    ),
                    MessageTemplateAction(
                        label='即時統計',
                        text='@計算中稍等一下喔~'
                    ),
                    MessageTemplateAction(
                        label='預算功能',
                        text='@預算'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage('發生錯誤！請稍後再試'))

def accounting_clean_check(event):
    try:
        message = TemplateSendMessage(
            alt_text='花費紀錄刪除確認按鈕',
            template=ConfirmTemplate(
                text='確定要刪除?',
                actions=[
                    MessageTemplateAction(
                        label='確定刪除',
                        text='@確認刪除花費'
                    ),
                    MessageTemplateAction(
                        label='取消',
                        text='取消'
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！請稍後再試'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)








