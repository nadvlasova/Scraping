import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pprint import pprint
from pymongo import MongoClient

# Создаем БД
client = MongoClient('127.0.0.1', 27017)
db = client['m_video']
tr_line = db.tr_line

chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')

driver = webdriver.Chrome ('./chromedriver', options=chrome_options)
# driver = webdriver.Chrome (executable_path='./chromedriver')
driver.get('https://www.mvideo.ru/')
wait = WebDriverWait(driver, 30)

btn = wait.until(EC.presence_of_element_located((By.XPATH, '//mvid-icon[contains(@class, "modal-layout__close ng-tns-c72-1 ng-star-inserted")]')))
btn.click()
time.sleep(5)

# скрол до кнопки "в тренде"
driver.execute_script('window.scrollTo(0, 1500);')
time.sleep(5)

# кликаем на кнопку "в тренде"
el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//mvid-shelf-group/*//span[contains(text(), "В тренде")]')))
el.click()

# Кликаем на стрелку вправо, пока она не скроется прогружаем все товары в линейке "в тренде"
while True:
    try:
        btn = driver.find_elements(By.XPATH, '//mvid-shel-group/*//button[contains(@class, "btn forward")]/mvid-icon[@type = "chevron_right"]')
        btn[1].click()
        time.sleep(5)
    except selenium.common.exceptions.ElementNotInteractableException:
        break

# выбираем все ссылки на блоки с товарами
items = driver.find_elements(By.XPATH, '//mvid-shelf-group//mvid-product-cards-group//div[@class="title"]')

#_____!!!!! Сделала сначала так, но!!! по этой ссылку мало информации, я правильно понимаю тут в цикле нужно прописывать
#_____!!!!! клик по ссылке, заходить на страничку каждого товара и с неё уже вытаскивать подробную информацию, цену и т.д.


# итерируемся по списку ссылок вытаскивая информацию о каждом товаре
items_list = []
for item in items:
    item_info = {}
    item_link = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
    item_title = item.find_element(By.TAG_NAME, 'a').text

    item_info['Title'] = item_title
    item_info['Link'] = item_link

    items_list.append(item_info)

# складываем данные в БД
    tr_line.insert_one(item_info)
    tr_line.create_index('Link', unique=True)

pprint(items_list)
driver.close()
