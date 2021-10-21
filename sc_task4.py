import requests
from lxml import html
from pprint import pprint
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['lenta']
news_lenta = db.news_lenta

header = {"User Agent	Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"}

url = 'https://lenta.ru/'
response = requests.get(url)
dom = html.fromstring(response.text)  # из всего сайта строим дом и выбираем xpath раздел с новостями
items = dom.xpath("//div[contains(@class, 'b-yellow-box__wrap')]/div/a/@href")  # получаем ссылки на объекты каждой новости отдельно

all_news = []

for item in items:
    news = {}
    url_news = url + item  # составляем ссылку, чтобы сделать get запрос на страницу каждой новости
    response_news = requests.get(url_news)
    dom_news = html.fromstring(response_news.text)  # строим дом страницы отдельной новости
    items2 = dom_news.xpath("//div[@class='b-topic__content']")  # выбираем блок в котором есть название и дата
    for it in items2:
        title = it.xpath("//h1/text()")  # получаем заголовок новости
        link = url_news  # ссылку берем выше, по которой переходили на страницу новости
        date = it.xpath("//div//div[@class='b-topic__info']/time/@datetime")  # получаем дату

    news['title'] = title[0].replace("\xa0", " ")
    news['link'] = link
    news['date'] = date

    all_news.append(news)

    news_lenta.insert_one(news)
    for doc in news_lenta.find({}):
        pprint(doc)
    pprint(all_news)
    pprint(len(all_news))




