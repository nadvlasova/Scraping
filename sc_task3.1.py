# https://irkutsk.hh.ru/vacancies/svarshik

import requests
from bs4 import BeautifulSoup as bs
import re
from pymongo import MongoClient
import pprint


def isint(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# проверка на наличие записи в БД
def check(s):
    for doc in hh_vacancy.find({'link': s}):
        return True


# подключение БД
client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
hh_vacancy = db.hh_vacancy

vacancy_user = input('Введите вакансию: ')

url = 'https://hh.ru/search/vacancy'

params = {
    'text': vacancy_user,
    'page': 1}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

while True:
    response = requests.get(url, params=params, headers=headers)
    soup = bs(response.text, 'html.parser')

    vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
    if not vacancy_list or not response.ok:
        break
    # print(vacancy_list[0])
    vacancies = []

    for vacancy in vacancy_list:

        info_group = {}

        vacancy_info = vacancy.find('a', attrs={'class': 'bloko-link'})
        vacancy_name = vacancy_info.text
        vacancy_link = vacancy_info['href']
        vacancy_town = vacancy.find('span', attrs={'class': 'vacancy-serp-item__meta-info'}).text
        company_link = vacancy.find('div', attrs={'class': 'vacancy-serp-item__meta-info-company'}).a["href"]
        salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        if not salary:
            salary_min = None
            salary_max = None
            salary_currency = None
        else:
            salary = salary.getText() \
                .replace(u'\xa0', u'')

            salary = re.split(r'\s|<|>', salary)

            if salary[0] == 'до':
                salary_min = None
                if isint(salary[1]) and isint(salary[2]):
                    salary_max = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_max = int(salary[1])
                    salary_currency = salary[2]
            elif salary[0] == 'от':
                if isint(salary[1]) and isint(salary[2]):
                    salary_min = int("".join([salary[1], salary[2]]))
                    salary_currency = salary[3]
                else:
                    salary_min = int(salary[1])
                    salary_currency = salary[2]
                salary_max = None
            else:
                if isint(salary[0]) and isint(salary[1]):
                    salary_min = int("".join([salary[0], salary[1]]))
                    if isint(salary[3]) and isint(salary[4]):
                        salary_max = int("".join([salary[3], salary[4]]))
                        salary_currency = salary[5]
                    else:
                        salary_max = int(salary[3])
                        salary_currency = salary[4]
                else:
                    salary_min = int(salary[0])
                    if isint(salary[2]) and isint(salary[3]):
                        salary_max = int("".join([salary[2], salary[3]]))
                        salary_currency = salary[4]
                    else:
                        salary_max = int(salary[2])
                        salary_currency = salary[3]

        info_group['name'] = vacancy_name
        info_group['link'] = vacancy_link
        info_group['town'] = vacancy_town
        info_group['companyLink'] = company_link
        info_group['salary'] = salary

        params['page'] += 1

        # Проверка наличия такой записи в БД
        if check(info_group['link']) is True:
            continue
        else:
            hh_vacancy.insert_one(info_group)

        vacancies.append(info_group)
        pprint(info_group)
