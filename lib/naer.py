# -*- coding: utf-8 -*-
import re, sys
import time, random
import json
import copy
import chardet
import requests
import telnetlib
from bs4 import BeautifulSoup as bs
import multiprocessing as mp
from multiprocessing import Pool
from fake_useragent import UserAgent
try:
    from lib.freeproxy import freeproxy
    from lib.config import Config
except:
    from freeproxy import freeproxy
    from config import Config

class naer:
    ''' [class] '''

    def __init__(self):
        self.options = {}
        self.cfg = Config()
        self.cur_page = int(self.cfg.get('control')['indexpage'])
        self.page = 0
        self.base_url = 'http://terms.naer.edu.tw/search/'
        self.proxy_switch = False
        self.proxies = self.get_proxy()
        self.result = self.gather()

    ''' 取得 page 的 encoding '''
    def get_encoding(self, response):
        encoding = ''
        if re.findall(r'(?i)(?:charset=.*)', response.headers['content-type'], re.I&re.U):
            content_type = [ i.strip() for i in response.headers['content-type'].split('charset=') ]
            try:
                encoding = content_type[1]
            except Exception as e:
                raise e
        else:
            encoding = chardet.detect(response.content)["encoding"]
        return encoding

    def set_proxy_switch(self, proxy=None):
        if not proxy:
            self.proxy = False
        else:
            self.proxy = proxy

    def fetch(self, url=None, params=None, proxy=False):
        content = ''
        encoding = ''
        if url and params:
            if proxy==False:
                with requests.session().get(url = url, headers = {'headers':UserAgent().random}, params = params, stream=True) as req:
                    if req.status_code == 200:
                        try:
                            encoding = self.get_encoding(req)
                            content = req.content.decode(encoding, errors='ignore')
                        except:
                            try:
                                content = req.content.decode('gb2312', errors='ignore')
                            except Exception as e:
                                raise e
            else:
                try:
                    with requests.session().get(url = url, headers = {'headers':UserAgent().random}, params = params, stream=True, proxies=self.proxies, timeout=3) as req:
                        if req.status_code == 200:
                            try:
                                encoding = self.get_encoding(req)
                                content = req.content.decode(encoding, errors='ignore')
                            except:
                                try:
                                    content = req.content.decode('gb2312', errors='ignore')
                                except Exception as e:
                                    raise e
                except:
                    with requests.session().get(url = url, headers = {'headers':UserAgent().random}, params = params, stream=True) as req:
                        if req.status_code == 200:
                            try:
                                encoding = self.get_encoding(req)
                                content = req.content.decode(encoding, errors='ignore')
                            except:
                                try:
                                    content = req.content.decode('gb2312', errors='ignore')
                                except Exception as e:
                                    raise e
        else:
            raise NameError('url ,headers and params must fill in a value')
        return (content)

    def parse(self, content):
        result = []
        try:
            soup = bs(content, 'html.parser')
            self.page = int(soup.select('#id_page')[0].text.strip()[1:-1])
            for items in soup.select(".dash"):
                idx = items.select("label")[0].text.replace('\n','').strip()
                val = items.select(".resultcheckbox ")[0]['value']
                data = [item.text for item in items.select("td")[:] ]
                category = data[0].replace('\n','')
                en = data[1].replace('\n','')
                ch = data[2].replace('\n','')
                result.append([idx, val, category, en, ch])
        except Exception as e:
            raise e
        return (result)

    def gather(self):
        lists = []
        try:
            self.options = {'q':'','num':'50','page':''+str(self.cur_page)+''}
            content = self.fetch(self.base_url, self.options, self.proxy_switch)
            lists = self.parse(content)
        except:
            print("Unexpected error:",sys.exc_info())
        print(lists)
        self.cfg.set('control','indexpage',str(self.cur_page+1 ))
        self.cfg.write()
        return (lists)

    def content2sql(self, words):
        return (words.replace('\'','\'\''))

    def check_proxy(self, cur_proxy):
        c_proxy = (cur_proxy.replace('https://','')).replace('http://','')
        proxy = c_proxy.split(':')
        ip = proxy[0]
        port = proxy[1]
        try:
            telnetlib.Telnet(ip, port=port, timeout=3)
        except:
            return False
        return True

    def get_proxy(self):
        fp = freeproxy()
        proxy = fp.cur_proxy
        while self.check_proxy(proxy):
            proxy = fp.get_proxy()
        dicts = {}
        if 'https' in proxy:
            dicts = {'https':proxy.replace('https://','')}
        else:
            dicts = {'http':proxy.replace('http://','')}
        return (dicts)

# def test():
#     url = 'http://terms.naer.edu.tw/search/'
#     params = {
#         'q':'',
#         'num':50,
#         'page':1
#     }

#     with requests.session().get(url = url, params = params, stream=True) as req:
#         if req.status_code == 200:
#             try:
#                 content = req.content.decode('utf-8', errors='ignore')
#             except Exception as e:
#                 raise e
#         # print(content)
#         result = []
#         soup = bs(content, 'html.parser')
#         page = soup.select('#id_page')[0].text.strip()[1:-1]
#         print(page)
#         for items in soup.select(".dash"):
#             idx = items.select("label")[0].text.replace('\n','').strip()
#             val = items.select(".resultcheckbox ")[0]['value']
#             data = [item.text for item in items.select("td")[:] ]
#             category = data[0].replace('\n','')
#             en = data[1].replace('\n','')
#             ch = data[2].replace('\n','')
#             result.append([idx, val, category, en, ch])
#         # print(result)

# if __name__ == '__main__':
#     test()