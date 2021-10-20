import scrapy
from scrapy.http import HtmlResponse
from lerua_merlen.items import LeruaMerlenItem
from scrapy.loader import ItemLoader


class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query):
        super().__init__()
        # self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']  # такой вариант у меня не сработал
        self.start_urls = ['https://leroymerlin.ru/catalogue/komnatnye-rasteniya-i-cvety/']  #  пришлось копировать строку из каталога

    def parse(self, response: HtmlResponse):  #  здесь pycharm предлагает дописать **kwargs пока не разобралась зачем
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@data-qa-product]/a")
        for link in links:
            yield response.follow(link, callback=self.parse_category)

    def parse_category(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaMerlenItem(), response=response)
        loader.add_value('link', response.url)
        loader.add_xpath('name', '//h1/text()')
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('photo', "//source[contains(@media, 'min-width: 1024')]/@srcset")
        yield loader.load_item()
