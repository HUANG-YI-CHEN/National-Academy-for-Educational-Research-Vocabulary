# -*- coding: utf-8 -*-
import os, re, sys
import time, random, datetime
import copy
import chardet
import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
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
        self.result = self.get()

    ''' 取得 page 的 encoding '''
    async def get_encoding(self, response):
        encoding = ''
        if not response.charset:
            try:
                content = await response.read()
                encoding = chardet.detect(content)["encoding"]
            except Exception as e:
                raise e
        else:
            encoding = response.charset
        return encoding

    def set_proxy_switch(self, proxy=None):
        if not proxy:
            self.proxy = False
        else:
            self.proxy = proxy

    async def fetch(self, url=None, params=None, proxy=False):
        # await asyncio.sleep(delay)
        content = ''
        encoding = ''
        if url and params:
            if proxy==False:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url=url, headers = {'headers':UserAgent().random}, params = params) as response:
                        if response.status == 200:
                            try:
                                encoding = await self.get_encoding(response)
                                content = await response.text(encoding)
                            except:
                                try:
                                    content = await response.text('cp950')
                                except:
                                    try:
                                        content = await response.text('gb2312')
                                    except Exception as e:
                                        raise e
            else:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=url, headers = {'headers':UserAgent().random}, params = params, proxy=self.proxies, timeout=3) as response:
                            if response.status == 200:
                                try:
                                    encoding = await self.get_encoding(response)
                                    content = await response.text(encoding)
                                except:
                                    try:
                                        content = await response.text('cp950')
                                    except:
                                        try:
                                            content = await response.text('gb2312')
                                        except Exception as e:
                                            raise e
                except:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url=url, headers = {'headers':UserAgent().random}, params = params) as response:
                            if response.status == 200:
                                try:
                                    encoding = await self.get_encoding(response)
                                    content = await response.text(encoding)
                                except:
                                    try:
                                        content = await response.text('cp950')
                                    except:
                                        try:
                                            content = await response.text('gb2312')
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

    async def gather(self, loop):
        lists = []
        try:
            self.options = {'q':'','num':'50','page':''+str(self.cur_page)+''}
            content = await self.fetch(self.base_url, self.options, self.proxy_switch)
            lists = self.parse(content)
        except:
            print("Unexpected error:",sys.exc_info())

        return (lists)

    def get(self):
        dicts = []
        # Asyncio Event Loop is Closed : https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed
        # loop = asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        dicts = loop.run_until_complete(self.gather(loop))
        loop.close()
        return (dicts)

    def write_config(self, page):
        self.cfg.set('control','indexpage',str(page))
        self.cfg.write()

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
            if 'https' in proxy:
                proxy = fp.get_proxy()
        return (proxy)

# def test():
#     a = naer()
#     print(a.result)
#     print(a.page)

# if __name__ == '__main__':
#     test()
