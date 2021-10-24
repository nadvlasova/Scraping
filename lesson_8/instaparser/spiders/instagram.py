import scrapy
import re
import json
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'  # Qw123456789
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1634577477:AWdQAK0AEOF+wFwWVYjoEuu8uCHn+Pabck9vUxQlFS3/o3VdiZCGuEm4HaF+MLP9EwSytUXe+VNGZWVqv/Pz+z14vr8gT4dClBa6OPYXzPbHCHcU0fUqrO731Bcf4OCxjIcxB4lurkTpWrZPz+Ir'

    # user_for_parse = 'ai_machine_learning'
    # graphql_url = 'https://www.instagram.com/graphql/query/?'
    # posts_hash = '8c2a529969ee035a5063f2fc8602a0fd'

    # инициализируем список пользователей к которым можно будет зайти на страницу
    def __init__(self, users_for_parse):
        super(InstagramSpider, self).__init__()
        self.users_for_parse = users_for_parse

    # авторизуемся
    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf}
        )

    # идем на страницу пользователя
    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:  # проверка, что авторизация прошла успешно
            for user in self.users_for_parse:
                yield response.follow(
                    f'/{user}',  # получаем относительную ссылку страницы пользователя к которому пойдем на страницу
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    # собираем данные со страницы пользователя
    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        followers_url = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page'
        yield response.follow(followers_url,
                              callback=self.users_followers,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         }
                              )
        following_url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12'
        yield response.follow(following_url,
                              callback=self.users_following,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         }
                              )

    def users_followers(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        page_info = j_data.get('next_max_id')
        if page_info:
            followers_url = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&max_id={page_info}&search_surface=follow_list_page'
            yield response.follow(followers_url,
                                  callback=self.users_followers,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             }
                                  )
            users = j_data.get('users')
            for user in users:
                item = InstaparserItem(userid=user_id,
                                       user_id=user.get('pk'),
                                       user_name=username,
                                       user_nik=user.get('username'),
                                       user_photo=user.get('profile_pic_url'),
                                       follow_flag=True
                                       )
                yield item

    def users_following(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        page_info = j_data.get('next_max_id')
        if page_info:
            following_url = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=12&max_id={page_info}'
            yield response.follow(following_url,
                                  callback=self.users_following,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             }
                                  )
            users = j_data.get('users')
            for user in users:
                item = InstaparserItem(userid=user_id,
                                       user_id=user.get('pk'),
                                       user_name=username,
                                       user_nik=user.get('username'),
                                       user_photo=user.get('profile_pic_url'),
                                       follow_flag=False
                                       )
                yield item

    # функция для получения csrf, в качестве параметра принимает response.text, распарсивает с помощью регулярных выражений и выдает отформатированный csrf
    # который мы используем для авторизации
    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
