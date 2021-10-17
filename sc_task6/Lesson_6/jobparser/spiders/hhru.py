import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?fromSearchLine=true&text=Python&from=suggest_post&area=1&search_field=description&search_field=company_name&search_field=name',
                  'https://hh.ru/search/vacancy?fromSearchLine=true&text=Python&from=suggest_post&area=2&search_field=description&search_field=company_name&search_field=name']

    def parse(self, response:HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()  # получили относительную ссылку на кнопку Далее для перехода на следующую страницу поиска
        if next_page:  # проверка на наличие кнопки Далее для перелистывания страниц поиска
            yield response.follow(next_page, callback=self.parse)  # если страница есть применяем к ней метод parse

        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1[@data-qa='vacancy-title']/text()").get()
        salary = response.xpath("//p[@class='vacancy-salary']/span/text()").getall()
        link = response.url
        # experiense_busyness = response.xpath("//div[@class='vacancy-description']/div[@class='bloko-gap bloko-gap_bottom']/p/text()").get() # опыт, занятость
        # description = response.xpath("//div//div[@class='g-user-content']/text).getall() # описание вакансии
        item = JobparserItem(name=name, salary=salary, link=link)
        yield item

