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


def get_week_log_date():
    today = datetime.today()
    todayData = pd.read_csv(f'./kafka_consumer_data/user_rs_log_{today.year}-{today.month}-{today.day}.csv', encoding='utf-8', header=None)
    for i in range(1, 7):
        try:
            data = pd.read_csv(f'./kafka_consumer_data/user_rs_log_{today.year}-{today.month}-{today.day-i}.csv', encoding='utf-8', header=None)
            todayData = pd.concat([todayData, data], axis=0)
        except FileNotFoundError:
            pass
    return todayData

def get_top5_hotel():
    data = get_week_log_date()
    top5_hotels = data.groupby(1, as_index=0).count().sort_values(by=0, ascending=0).iloc[:5,0]
    top5 = [hotel for hotel in top5_hotels]
    return top5

def get_top5_url(top5):
    tmpList = list()
    conn, cursor = conn_mysql(host='10.2.16.174', user='tfb1031_12', pwd='qwe123456', db='tfb1031_project')
    for hotel in top5:
        sql = f'SELECT bnb_url FROM bnb WHERE bnb_name = "{hotel}";'
        cursor.execute(sql)
        try:
            tmpList.append(cursor.fetchall()[0][0])
        except IndexError:
            # If url is empty, return home page
            tmpList.append('https://www.booking.com/index.zh-tw.html')
    close_conn_mysql(conn, cursor)
    return tmpList

def get_hotRank_button():
    top5 = get_top5_hotel()        # top5 = [hotel_1, hotel_2, hotel_3, hotel_4, hotel_5]
    top5_url = get_top5_url(top5)  # url = [url_1, url_2, url_3, url_4, url_5]
    button = json.load(open('./line_bot_card/card_hotRank_button.json', 'r', encoding='utf-8'))
    for i in range(0, 5):
        button['footer']['contents'][i]['action']['label'] = top5[i]
        button['footer']['contents'][i]['action']['uri'] = top5_url[i]
    return button

