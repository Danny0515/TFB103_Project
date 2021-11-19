import configparser
from linebot import LineBotApi, WebhookHandler
from datetime import datetime
import pandas as pd
import json
from app_accounting import conn_mysql, close_conn_mysql


config = configparser.ConfigParser()
config.read('./config/config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

def get_restaurant(area):
    conn, cursor = conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='tfb1031_project')
    sql = f'''
    SELECT res_name, image_url, article_url, address FROM test_restaurant
        WHERE area = "{area}"
        ORDER BY score DESC
        LIMIT 5;'''
    cursor.execute(sql)
    result = cursor.fetchall()
    restaurant_dict = {key[0]: key[1:] for key in result}
    close_conn_mysql(conn, cursor)
    return restaurant_dict

def get_restaurant_query_button(area):
    button = json.load(open('./line_bot_card/card_restQuery_button.json', 'r', encoding='utf-8'))
    restaurant_dict = get_restaurant(area)
    for i, restaurant in enumerate(restaurant_dict.items()):
        # restaurant name
        button['contents'][i]['body']['contents'][0]['text'] = restaurant[0]
        # restaurant image_url
        button['contents'][i]['hero']['url'] = restaurant[1][0]
        # restaurant article_url
        button['contents'][i]['footer']['contents'][0]['action']['uri'] = restaurant[1][1]
        # restaurant address
        if len(restaurant[1][2]) < 18:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] = restaurant[1][2]
        else:
            button['contents'][i]['body']['contents'][2]['contents'][0]['contents'][0]['text'] \
                = restaurant[1][2][:17] + '...'
    return button


