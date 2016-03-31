import requests


class DoubanClient(object):
    
    URL = 'http://api.douban.com'

    def __init__(self, app_key):
        self.app_key = app_key

    def get_book_by_id(self, db_id):
        resp = requests.get(DoubanClient.URL + '/book/subject/%s' % db_id, 
                            params={'alt': 'json', 'apikey': self.app_key})
        return resp.text

    def get_book_by_isbn(self, isbn):
        resp = requests.get(DoubanClient.URL + '/book/subject/isbn/%s' % isbn, 
                            params={'alt': 'json', 'apikey': self.app_key})
        return resp.text

