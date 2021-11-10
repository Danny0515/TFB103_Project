import time
import pymongo
import requests
from bs4 import BeautifulSoup
import json
from pymongo.errors import BulkWriteError
from requests.exceptions import MissingSchema


# information for mongodb atlas or local server
conn_str = "mongodb://tfb1031:qwe123456@10.2.16.174/raw_data_for_project"  # local server
# conn_str = 'mongodb+srv://danny:qwe123456@cluster0.er4zj.mongodb.net/raw_data_for_project?ssl=true&ssl_cert_reqs=CERT_NONE'
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=20000)
db = client.get_database('raw_data_for_project')
collection = db.pixnet_test
mongo_index_id = 0


# information for session
userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

headers = {
    "user-Agent": userAgent,
    "Referer": 'https://www.pixnet.net/'
}

# landingPage_url = 'https://www.pixnet.net/tags/%E4%BD%8F%E5%AE%BF?utm_source=PIXNET&utm_medium=navbar&utm_term=search_result_tag&utm_content=%E4%BD%8F%E5%AE%BF'


# crawler for 3 LandingPage with different keyword
for webTime in range(1,4):
    emptyPage_count = 0
    tmpData = list()
    page = 1
    ss = requests.session()
    if webTime == 1:
        # keyword = '住宿'
        # url = f'https://www.pixnet.net/mainpage/api/tags/%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest&refer=https%3A%2F%2Fwww.pixnet.net%2F%3Futm_source%3DPIXNET%26utm_medium%3Dnavbar%26utm_term%3Dhome'
        url = f'https://www.pixnet.net/mainpage/api/tags/%E5%8F%B0%E5%8C%97%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
    elif webTime == 2:
        # keyword = '民宿'
        # url = f'https://www.pixnet.net/mainpage/api/tags/%E6%B0%91%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
        url = f'https://www.pixnet.net/mainpage/api/tags/%E6%96%B0%E5%8C%97%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
    else:
        # keyword = '飯店'
        # url = f'https://www.pixnet.net/mainpage/api/tags/%E9%A3%AF%E5%BA%97/feeds?page={page}&per_page=5&filter=articles&sort=latest'
        url = f'https://www.pixnet.net/mainpage/api/tags/%E5%AE%9C%E8%98%AD%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'

    # crawler until empty pages = 20
    while emptyPage_count != 20:
        try:
            res_pixnet = ss.get(url, headers=headers)
        except:
            print('Url connect error, try it again after 5 seconds')
            time.sleep(5)
            continue
        try:
            pixnet_html = res_pixnet.text
            json_data = json.loads(pixnet_html)

            for data in json_data['data']['feeds']:
                title = data['title']
                author = data['display_name']
                member_uniqid = data['member_uniqid']
                articleUrl = data['link']
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['created_at']))
                tags = data['tags']
                hit = data['hit']
                reply_count = data['reply_count']
                poi = data['poi']

                # request for pixnet article page
                res_pixnetArticle = ss.get(articleUrl, headers=headers)
                pixnetArticle_html = res_pixnetArticle.text
                pixnetArticle_html = pixnetArticle_html.encode('ISO-8859-1')
                pixnetArticle_html = pixnetArticle_html.decode('utf-8')
                article_html = BeautifulSoup(pixnetArticle_html, 'html.parser')

                # get article content & imgUrl
                content = article_html.select('div[class="article-content"]')[0].text
                imgUrl =[url['src'] for url in article_html.select('img[loading="lazy"]')]

                # set data to dict for mongodb
                tmpDict_for_mongo = {
                    '_id': f'pixnet_hotel_{mongo_index_id}',
                    'title': title,
                    'author': author,
                    'member_uniqid': member_uniqid,
                    'articleUrl': articleUrl,
                    'date': date,
                    'tags': tags,
                    'hit': hit,
                    'reply_count': reply_count,
                    'poi': poi,
                    'content': content,
                    'imgUrl': imgUrl
                }
                mongo_index_id += 1
                tmpData.append(tmpDict_for_mongo)

        # if the article or the page is empty
        except (KeyError, IndexError, MissingSchema):
            pass

        print("finish page {}".format(page))
        page += 1
        if webTime == 1:
            # url = f'https://www.pixnet.net/mainpage/api/tags/%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest&refer=https%3A%2F%2Fwww.pixnet.net%2F%3Futm_source%3DPIXNET%26utm_medium%3Dnavbar%26utm_term%3Dhome'
            url = f'https://www.pixnet.net/mainpage/api/tags/%E5%8F%B0%E5%8C%97%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
        elif webTime == 2:
            # url = f'https://www.pixnet.net/mainpage/api/tags/%E6%B0%91%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
            url = f'https://www.pixnet.net/mainpage/api/tags/%E6%96%B0%E5%8C%97%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'
        else:
            # url = f'https://www.pixnet.net/mainpage/api/tags/%E9%A3%AF%E5%BA%97/feeds?page={page}&per_page=5&filter=articles&sort=latest'
            url = f'https://www.pixnet.net/mainpage/api/tags/%E5%AE%9C%E8%98%AD%E4%BD%8F%E5%AE%BF/feeds?page={page}&per_page=5&filter=articles&sort=latest'

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
                    time.sleep(7)
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
                                    time.sleep(7)
                                except pymongo.errors.BulkWriteError as pymongoError:
                                    print('second time insert & drop this tmpData')
                                    tmpData = list()
                            else:
                                pass


# collection.delete_many({})
print('目前已存入', collection.count_documents({}), '筆資烙')
client.close()
