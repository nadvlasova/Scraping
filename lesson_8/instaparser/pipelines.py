# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.instagram

    def process_item(self, item, spider):
        collection = self.db[item.get('user_name')]
        collection.update_one({'user_id': item['user_id'], 'follow_flag': item['follow_flag']},
                              {'$set': item}, upset=True)
        return item

    class InstaImagesPipeline(ImagesPipeline):
        def get_media_requests(self, item, info):
            if item['user_photo']:
                try:
                    yield scrapy.Request(item['user_photo'])
                except Exception as e:
                    print(e)

        def item_completed(self, results, item, info):
            item['user_photo'] = [itm[1] for itm in results if itm[0]]
            return item

        def file_path(self, request, response=None, info=None, *, item=None):
            if item['follow_flag']:
                image_path = item['user_name'] + '/followed'
                image_guid = item['username'] + '.jpg'
            else:
                image_path = item['user_name'] + '/follows'
                image_guid = item['username'] + '.jpg'
            return f'{image_path}{image_guid}'


