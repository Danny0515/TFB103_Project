'''
document = https://docs.mongodb.com/drivers/pymongo/
youtube參考影片 = https://www.youtube.com/watch?v=VQnmcBnguPY
pip install pymongo[srv]
上半部是官方文件說明的內容，下半部可以直接複製 code
'''

import pymongo
from pymongo.server_api import ServerApi  # for set api version

# Replace the uri string with your MongoDB deployment's connection string.
conn_str = "mongodb+srv://<username>:<password>@<cluster-address>/test?retryWrites=true&w=majority"

# create conn & set a 5-second connection timeout
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
# 自行設定 server_api 版本才用下面這行
# client = pymongo.MongoClient(conn_str, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)

# If the connection succeeds, you can see this db's info
try:
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")


# ===================== 下面直接複製就可以丟資料到 mongo atlas server =====================
import pymongo

conn_str = 'mongodb+srv://tfb103_g1:qwe123456@cluster0.fcab5.mongodb.net/raw_data_for_project?retryWrites=true&w=majority'
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)

# 連線到 db (db名稱 = raw_data_for_project)
db = client.get_database('raw_data_for_project')
# 賦予 collection 一個變數，才可以呼叫 pymongo method
collection = db.改成你的collection名稱
'''
各網站的 collection (就是 Justin 說的桶子)名稱如下:
==================
愛食記 = ifoodie
波波黛莉 = popdaily
hotel.com = hotel
痞客邦 = pixnet
背包客棧 = backpackers
低卡dcard = dcard
ptt = ptt 
=================
'''
# 查看 collection 內的資料筆數
collection.count_documents({})

# 輸入的資料格式參考，用 list 包 dict 就可以丟多筆
data = [
    {
        "title": "我是標題",
        "author": "我是作者",
    },
    {
        "title": "我也是標題",
        "author": "我也是作者",
    }
]

# 新增一筆資料
collection.insert_one(data)
# 新增多筆資料
collection.insert_many(data)
# 清空 collection
collection.remove({})