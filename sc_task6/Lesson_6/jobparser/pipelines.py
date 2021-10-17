# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)  # подключаемся к БД
        self.mongo_base = client.vacancy1110  # создаем БД с именем client.vacancy1110

    # функция структурирования всех данных
    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_hhru(item['salary'])
            del item['salary']
        elif spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_sjru(item['salary'])
            del item['salary']

        collection = self.mongo_base[spider.name]  # указатель на коллекцию, имя паука, чтобы данные разных пауков раскидывались по своим БД
        collection.insert_one(item)  # добавляем данные в БД
        return item

    # функция обработки внешнего вида строки зарплата
    def process_salary_hhru(self, salary):
        if salary == ['з/п не указана']:
            salary_min = None
            salary_max = None
            currency = None
        else:
            if salary[0] == 'до':
                salary_max = int(salary[1].replace('\xa0', ''))
                salary_min = None
            elif (salary[0] == 'от ') and ((' до ') not in salary):
                salary_min = int(salary[1].replace('\xa0', ''))
                salary_max = None
            else:
                salary_min = int(salary[1].replace('\xa0', ''))
                salary_max = int(salary[3].replace('\xa0', ''))
# валюту хотелось всю по индексам разобрать и собрать, но опыта недостаточно боюсь пока сломать то, что работает
            if 'руб.' in salary:
                currency = 'руб.'
            elif 'USD' in salary:
                currency = 'USD'
            elif 'EUR' in salary:
                currency = 'EUR'
            else:
                currency = None
        return salary_min, salary_max, currency

    def process_salary_sjru(self, salary):
        if salary == ['По договоренности']:
            salary_min = None
            salary_max = None
            currency = None
        else:
            if salary[0] == 'до':
                salary = salary[2].split('\xa0')
                salary_max = int(salary[0] + salary[1])
                salary_min = None
                currency = salary[-1]
            elif salary[0] == 'от':
                salary = salary[2].split('\xa0')
                salary_min = int(salary[0] + salary[1])
                salary_max = None
                currency = salary[-1]
            else:
                salary_min = int(salary[0].replace('\xa0', ''))
                salary_max = int(salary[1].replace('\xa0', ''))
                currency = salary[-1]
            return salary_min, salary_max, currency














