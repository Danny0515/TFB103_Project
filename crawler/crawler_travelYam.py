import time
import pymongo
import requests
import re
from bs4 import BeautifulSoup
from pymongo.errors import BulkWriteError
from requests.exceptions import MissingSchema


tmpData = list()
emptyPage_count = 0
mongo_index_id = 1

# information for mongodb atlas or local server
conn_str = "mongodb://tfb1031:qwe123456@10.2.16.174/raw_data_for_project"  # local server
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=20000)
db = client.get_database('raw_data_for_project')
collection = db.travelYam_hotel

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
headers = {
    "user-Agent": userAgent,
    "Referer": "https://travel.yam.com/info.aspx?i=4&tp=1"
}

page = 1
url = f'https://travel.yam.com/info.aspx?p={page}&tp=1&i=4'
ss = requests.session()

for i in range(1, 91):
    try:
        res_travelYam = ss.get(url, headers=headers)
        travelYam_html = BeautifulSoup(res_travelYam.text, 'html.parser')

        for index, html in enumerate(travelYam_html.select('div[class="left"]')):
            if index < 8:
                author = html.select('span')[0].text.split(': ')[1]
                date = html.select('time')[0].text
                articleUrl = 'https://travel.yam.com/' + html.select('a')[0]['href']

                # request for travelYam article page
                res_travelYamArticle = ss.get(articleUrl, headers=headers)
                travelYamArticle_html = BeautifulSoup(res_travelYamArticle.text, 'html.parser')

                # get article title, tags, content, imgUrl
                title = ''.join(re.findall('[^\s]', travelYamArticle_html.select('title')[0].text))
                tags = [tag.text for tag in travelYamArticle_html.select('span[class="name"]')]
                content = "".join([i.text for i in travelYamArticle_html.select('p')])
                imgUrl = [imgUrl['data-original'] for imgUrl in
                           travelYamArticle_html.select('div[id="mainArticleWrap"]')[0].select('img')]

                # set data to dict for mongodb
                tmpDict_for_mongo = {
                    '_id': f'travelYam_hotel_{mongo_index_id}',
                    'title': title,
                    'author': author,
                    'articleUrl': articleUrl,
                    'date': date,
                    'tags': tags,
                    'content': content,
                    'imgUrl': imgUrl
                }
                mongo_index_id += 1
                tmpData.append(tmpDict_for_mongo)

    except (KeyError, IndexError, MissingSchema):
        pass

    print("finish page {}".format(page))
    page += 1
    url = f'https://travel.yam.com/info.aspx?p={page}&tp=1&i=4'

    # insert data to mongodb, if there is duplicate, drop it from tmpData
    if page % 10 == 0:
        if len(tmpData) == 0:
            emptyPage_count += 1
            print('==================================')
            print('emptyPage =', emptyPage_count)
        else:
            try:
                collection.insert_many(tmpData)
                print('data_counts =', len(tmpData))
                print('==================================')
                print('目前已存入', collection.count_documents({}), '筆資烙')
                tmpData = list()
                time.sleep(10)
            # delete error data from tmpData
            except pymongo.errors.BulkWriteError as pymongoError:
                for errorMsg in pymongoError.details['writeErrors']:
                    errorTitle = errorMsg['op']['title']
                    print('文章重複： ', errorTitle)
                    print('目前筆數： ', len(tmpData))
                    for index, singleData in enumerate(tmpData):
                        if singleData['title'] == errorTitle:
                            tmpData.pop(index)
                            print('刪除後筆數: ', len(tmpData))
                            try:
                                collection.insert_many(tmpData)
                                print('data_counts =', len(tmpData))
                                print('==================================')
                                print('目前已存入', collection.count_documents({}), '筆資烙')
                                tmpData = list()
                                time.sleep(10)
                            except pymongo.errors.BulkWriteError as pymongoError:
                                print('second time insert & drop this tmpData')
                                tmpData = list()
                        else:
                            pass

# collection.delete_many({})
print('目前已存入', collection.count_documents({}), '筆資烙')
client.close()