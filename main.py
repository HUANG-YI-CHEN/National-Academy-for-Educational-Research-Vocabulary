# -*- coding: utf-8 -*-
import os, sys
import time
import random
import urllib
try:
    from lib.config import Config
    from lib.connect2sql import MSSQL
    from lib.naer_mult import naer
except:
    from config import Config
    from connect2sql import MSSQL
    from naer_mult import naer

clear = lambda: os.system( 'cls' )
unicode_cmd = lambda: os.system( 'chcp 65001 &' )

def timespent(calls):
    start = time.time()
    # time.sleep( random.uniform(1, 3) )
    calls
    end = time.time()
    print ('Cost : %.4f'%( abs(end-start) ))

def processCrawler():
    # initalize variable
    cfg = Config()
    config = cfg.get('database')
    debug = int(cfg.get('control')['debug'])
    conn = MSSQL( hostname=config['hostname'], username=config['username'], password=config['password'], database=config['database'] )

    counter = 1
    # start
    while True:
        try:
            nr = naer()
            for i in nr.result:
                if debug == 1:
                    print(i)
                sql = """
                    declare @idx int = %s
                    declare @val int = %s
                    declare @category nvarchar(max) = N'%s'
                    declare @ename nvarchar(max) = '%s'
                    declare @cname nvarchar(max) = N'%s'
                    exec dbo.xp_insertObjectData @idx, @val, @category, @ename, @cname
                    """%( i[0], i[1], nr.content2sql(i[2]), nr.content2sql(i[3]), nr.content2sql(i[4]) )
                try:
                   conn.execNonQuery(sql)
                except Exception as e:
                    raise e
                counter += 1
            # all transaction are ok, then update cur_page
            nr.write_config(nr.cur_page+1)
            # sleep crawler time random between 1 and 2
            time.sleep( random.uniform(1, 2) )
            if counter%50==0 and debug == 1:
                clear()
            if nr.cur_page > nr.page:
                conn.close()
                break
        except Exception as e:
            conn.close()
            raise e

if __name__ == '__main__':
    processCrawler()