import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient

# client = MongoClient('127.0.0.1', 27017)
# db = client['lenta']
# news_lenta = db.news_lenta

header = {"User Agent	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"}

response = requests.get("https://lenta.ru/")
dom = html.fromstring(response.text)

items = dom.xpath("//section[@class='row b-top7-for-main js-top-seven']//div[@class='item'] | //div[@class='first-item']")

all_news = []

for item in items:
    news = {}

    name = 'lenta.ru'
    title = item.xpath("./a/text()")
    link = item.xpath("./@href/text()")
    date = item.xpath("./a/time/@datetime")

    news['name'] = name
    news['title'] = title
    news['link'] = title
    news['date'] = date
    all_news.append(news)

    # news_lenta.insert_one(news)
    # for doc in news_lenta.find({}):
    #     pprint(doc)
    pprint(all_news)
    # pprint(len(all_news))




