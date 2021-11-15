import re
import pymysql
from datetime import datetime
import datetime
import matplotlib.pyplot as plt
import os
import pyimgur
import io
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment


# GCP key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './config/app_accounting_key.json'

# Open txt file to identify items
with open('./jiebaDict/app_accounting_food.txt', 'r', encoding='utf-8') as f:
    food_item = f.read(-1)
with open('./jiebaDict/app_accounting_shopping.txt', 'r', encoding='utf-8') as f:
    shop_item = f.read(-1)
with open('./jiebaDict/app_accounting_live.txt', 'r', encoding='utf-8') as f:
    live_item = f.read(-1)
with open('./jiebaDict/app_accounting_transportation.txt', 'r', encoding='utf-8') as f:
    traffic_item = f.read(-1)
with open('./jiebaDict/app_accounting_entertainment.txt', 'r', encoding='utf-8') as f:
    ent_item = f.read(-1)
with open('./config/imgur.txt', 'r', encoding='utf-8') as f:
    imgurClientId = f.read(-1).split('\n')[1]

# Create a directory to save image
def accounting_mkdir():
    if not os.path.exists('./static/app_accounting'):
        os.mkdir('./static/app_accounting')

def conn_mysql(host='localhost', user='testuser', pwd='qwe123456', db='app_accounting'):
    conn = pymysql.connect(
        host=host, port=3306,
        user=user, passwd=pwd,
        db=db
    )
    cursor = conn.cursor()
    return conn, cursor

def close_conn_mysql(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()

def insert_mysql_accounting(user_id, itemCost, item):
    conn, cursor = conn_mysql()
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = 'INSERT INTO user_cost VALUES(%s, %s, %s, %s);'
    cursor.execute(sql, (user_id, itemCost, time, item))
    close_conn_mysql(conn, cursor)

def speech_text_clean(rawSpeechText):
    # split & replace raw speech text, transform to dict
    string = re.findall('[^\d]+', rawSpeechText.replace('塊', '').replace('元', ''))
    number = [int(i) for i in re.findall('\d+', rawSpeechText)]
    return dict(zip(string, number))  # speechText -> {'早餐': 100, '捷運': 70,}

def identify_items(user_id, speechText):
    tmpDict = {'food':0, 'shop':0, 'live':0, 'traffic':0, 'entertain':0, 'other':0}
    if len(speechText) != 0:
        foodCost_sum = sum([speechText[key] for key in speechText.keys() if key in food_item])
        tmpDict['food'] += foodCost_sum
        shopCost_sum = sum([speechText[key] for key in speechText.keys() if key in shop_item])
        tmpDict['shop'] += shopCost_sum
        liveCost_sum = sum([speechText[key] for key in speechText.keys() if key in live_item])
        tmpDict['live'] += liveCost_sum
        trafficCost_sum = sum([speechText[key] for key in speechText.keys() if key in traffic_item])
        tmpDict['traffic'] += trafficCost_sum
        entCost_sum = sum([speechText[key] for key in speechText.keys() if key in ent_item])
        tmpDict['entertain'] += entCost_sum
        all_items = food_item + shop_item + live_item + traffic_item + ent_item
        other_sum = sum([speechText[key] for key in speechText.keys() if key not in all_items])
        tmpDict['other'] += other_sum
        print(tmpDict)
    for item, cost in tmpDict.items():
        if (item == 'food') & (cost != 0):
            insert_mysql_accounting(user_id, foodCost_sum, 'food')
        elif (item == 'shop') & (cost != 0):
            insert_mysql_accounting(user_id, shopCost_sum, 'shop')
        elif (item == 'live') & (cost != 0):
            insert_mysql_accounting(user_id, liveCost_sum, 'live')
        elif (item == 'traffic') & (cost != 0):
            insert_mysql_accounting(user_id, trafficCost_sum, 'traffic')
        elif (item == 'entertain') & (cost != 0):
            insert_mysql_accounting(user_id, entCost_sum, 'entertain')
        elif (item == 'other') & (cost != 0):
            insert_mysql_accounting(user_id, other_sum, 'other')
    else:
        errorMsg = '抱歉我沒聽清楚QQ，麻煩再說一次~ 謝謝'
        return errorMsg

def edit_budget(user_id, TextMessage):
    conn, cursor = conn_mysql()
    if 'ex:「新增預算' not in TextMessage:
        if '新增預算' in TextMessage:
            try:
                budget = re.findall('\d+', TextMessage)[0]
                sql = 'UPDATE user_info SET budget = %s WHERE user_id = %s;'
                cursor.execute(sql, (budget, user_id))
                close_conn_mysql(conn, cursor)
                return f'新增成功，目前預算:\n{budget}'
            except IndexError:
                return '輸入格式ex:「新增預算100000」'
        elif '修改預算' in TextMessage:
            try:
                budget = re.findall('\d+', TextMessage)[0]
                sql = 'UPDATE user_info SET budget = %s WHERE user_id = %s;'
                cursor.execute(sql, (budget, user_id))
                close_conn_mysql(conn, cursor)
                return f'修改成功，目前預算:\n{budget}'
            except IndexError:
                return '輸入格式ex:「修改預算100000」'
        elif '刪除預算' in TextMessage:
            sql = 'UPDATE user_info SET budget = %s WHERE user_id = %s;'
            cursor.execute(sql, (0, user_id))
            close_conn_mysql(conn, cursor)
            return '已刪除預算，記得輸入新預算，才能幫你算錢喔~'
        elif '查看預算' in TextMessage:
            sql = 'SELECT budget FROM user_info WHERE user_id = %s;'
            cursor.execute(sql, (user_id))
            budget = cursor.fetchall()[0][0]
            close_conn_mysql(conn, cursor)
            return f'目前預算: {budget}'
        else:
            msg = '可使用預算功能如下:\n1.新增預算\n2.修改預算\n3.刪除預算\n4.查看預算\n輸入格式ex:「新增預算100000」'
            return msg

def query_budget(user_id):
    conn, cursor = conn_mysql()
    sql_budget = f'SELECT budget FROM user_info WHERE user_id = "{user_id}";'
    cursor.execute(sql_budget)
    budget = cursor.fetchall()[0][0]
    sql_balance = f'SELECT sum(cost) FROM user_cost WHERE user_id = "{user_id}";'
    cursor.execute(sql_balance)
    balance = budget - cursor.fetchall()[0][0]
    close_conn_mysql(conn, cursor)
    return budget, balance

# Return msg before insert sql
# In case of spending too much time on querying
def response_user(user_id, speechText):
    if len(speechText) != 0:
        totalCost = sum([number for number in speechText.values()])
        budget, balance = query_budget(user_id)
        new_balance = budget - balance
        return f'本次花費:{totalCost}\n目前餘額:{new_balance}\n總預算:{budget}'
    else:
        errorMsg = '抱歉我沒聽清楚QQ，麻煩再說一次~\n謝謝'
        return errorMsg

# If (budget != 0) -> run program
def check_budget(user_id):
    conn, cursor = conn_mysql()
    sql = f'SELECT budget FROM user_info WHERE user_id = "{user_id}";'
    cursor.execute(sql)
    budget = cursor.fetchall()[0][0]
    close_conn_mysql(conn, cursor)
    if budget != 0:
        return True
    else:
        return False

def clean_budget(user_id):
    conn, cursor = conn_mysql()
    sql = f'DELETE FROM user_cost WHERE user_id = "{user_id}";'
    cursor.execute(sql)
    close_conn_mysql(conn, cursor)
    return '所有花費紀錄已刪除'

# Show pie chart
def accounting_statistics(user_id):
    budget, balance = query_budget(user_id)
    conn, cursor = conn_mysql()
    # Get all items cost from mysql
    sql_food = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_food, (user_id, 'food'))
    foodCost = cursor.fetchall()[0][0]
    if foodCost is None: foodCost = 0

    sql_shop = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_shop, (user_id, 'shop'))
    shopCost = cursor.fetchall()[0][0]
    if shopCost is None: shopCost = 0

    sql_live = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_live, (user_id, 'live'))
    liveCost = cursor.fetchall()[0][0]
    if liveCost is None: liveCost = 0

    sql_traffic = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_traffic, (user_id, 'traffic'))
    trafficCost = cursor.fetchall()[0][0]
    if trafficCost is None: trafficCost = 0

    sql_ent = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_ent, (user_id, 'entertain'))
    entCost = cursor.fetchall()[0][0]
    if entCost is None: entCost = 0

    sql_other = f'SELECT sum(cost) FROM user_cost WHERE user_id = %s and item = %s;'
    cursor.execute(sql_other, (user_id, 'other'))
    otherCost = cursor.fetchall()[0][0]
    if otherCost is None: otherCost = 0
    totalCost = sum([foodCost, shopCost, liveCost, trafficCost, entCost, otherCost])
    print(foodCost)
    print(shopCost)
    print(liveCost)
    print(trafficCost)
    print(entCost)
    print(otherCost)
    # Pie chart for all items cost
    fig = plt.figure(figsize=(7, 7))
    plt.pie(
        x=[foodCost/totalCost, shopCost/totalCost, liveCost/totalCost,
           trafficCost/totalCost, entCost/totalCost, otherCost/totalCost
           ],
        labels=['food', 'shop', 'live', 'traffic', 'entertainment', 'other'],
        colors=['palegoldenrod', 'burlywood', 'peru', 'chocolate', 'sienna', 'rosybrown'],
        autopct='%1.1f%%',
        normalize=False
    );
    plt.savefig(f'./static/app_accounting/pic_{user_id}.jpg')
    # Bar chart for budget
    if totalCost > budget:
        bar_color = 'red'
    else:
        bar_color = 'khaki'
    fig = plt.figure(figsize=(7, 7))
    plt.bar(
        height=[totalCost, budget],
        x=['already cost', 'budget'],
        color=[f'{bar_color}', 'powderblue']
    );
    plt.savefig(f'./static/app_accounting/bar_{user_id}.jpg')
    close_conn_mysql(conn, cursor)
    return foodCost, shopCost, liveCost, trafficCost, entCost, otherCost, totalCost

# Get image URL with imgur_api
def get_image_url(user_id):
    imgur = pyimgur.Imgur(client_id=imgurClientId)
    image1 = imgur.upload_image(f'./static/app_accounting/pic_{user_id}.jpg',
                                title=f'pie_{user_id}_1')
    image2 = imgur.upload_image(f'./static/app_accounting/bar_{user_id}.jpg',
                                title=f'pie_{user_id}_2')
    image1Url = image1.link
    image2Url = image2.link
    return image1Url, image2Url

def call_gcp_speech_to_ext(audio_wav):
    client = speech.SpeechClient()
    with io.open(audio_wav, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="zh-TW",
        enable_automatic_punctuation=True
        )
    response = client.recognize(config=config, audio=audio)
    for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        return alternative.transcript

# Convert acc to wav for GCP speech-to-text api
def covert_audio(user_id, rawAudio):
    rawAudioPath = './static/audio/{}.aac'.format(user_id)
    with open(rawAudioPath, 'wb') as f:
        for chunk in rawAudio.iter_content():
            f.write(chunk)
    newAudio = AudioSegment.from_file_using_temporary_files(rawAudioPath)
    newAudioPath = './static/audio/{}.wav'.format(user_id)
    newAudio.export(newAudioPath, format='wav')
    return newAudioPath

