# coding=utf-8
import tornado.httpclient


class BaseApi(tornado.httpclient.HTTPRequest):
    headers = {'Content-Type': 'application/octet-stream'}

    def __init__(self, url, body=None, **kwargs):
        super(BaseApi, self).__init__(url, body=body, method='POST', headers=self.headers, **kwargs)

    def parse_url(self):
        raise NotImplementedError

    def parse_body(self):
        raise NotImplementedError
