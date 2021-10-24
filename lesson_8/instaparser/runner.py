from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    users = input('user names for parse: ').split()

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider, users_for_parse=users)

    process.start()
