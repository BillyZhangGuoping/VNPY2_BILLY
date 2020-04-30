# encoding: UTF-8

from __future__ import print_function
import json
from datetime import datetime,date,timedelta
from time import time

from pymongo import MongoClient, ASCENDING

import sys
from threading import Thread
from queue import Queue, Empty
from copy import copy

from vnpy.event import Event, EventEngine
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.constant import Exchange
from vnpy.trader.object import (
    SubscribeRequest,
    TickData,
    BarData,
    ContractData
)
from vnpy.trader.event import EVENT_TICK, EVENT_CONTRACT
from vnpy.trader.utility import load_json, save_json, BarGenerator
from vnpy.trader.database import database_manager
from vnpy.app.spread_trading.base import EVENT_SPREAD_DATA, SpreadData


import jqdatasdk as jq

# 加载配置
config = open('config.json')
setting = json.load(config)

mc = MongoClient()  # Mongo连接


USERNAME = setting['Username']
PASSWORD = setting['Password']
jq.auth(USERNAME, PASSWORD)

FIELDS = ['open', 'high', 'low', 'close', 'volume']


# ----------------------------------------------------------------------
def generateVtBar(row, symbol):
    """生成K线"""
    bar = VtBarData()

    bar.symbol = symbol
    bar.exchange = "SHFE"
    bar.vtSymbol = bar.vtSymbol = '.'.join([bar.symbol, bar.exchange])
    bar.open = row['open']
    bar.high = row['high']
    bar.low = row['low']
    bar.close = row['close']
    bar.volume = row['volume']
    bardatetime = row.name
    bar.date = bardatetime.strftime("%Y%m%d")

    bar.time = bardatetime.strftime("%H%M%S")
    # 将bar的时间改成提前一分钟
    hour = bar.time[0:2]
    minute = bar.time[2:4]
    sec = bar.time[4:6]
    if minute == "00":
        minute = "59"

        h = int(hour)
        if h == 0:
            h = 24

        hour = str(h - 1).rjust(2, '0')
    else:
        minute = str(int(minute) - 1).rjust(2, '0')
    bar.time = hour + minute + sec

    bar.datetime = datetime.strptime(' '.join([bar.date, bar.time]), '%Y%m%d %H%M%S')
    return bar


# ----------------------------------------------------------------------
def jqdownloadMinuteBarBySymbol(symbol,startDate,endDate):
    """下载某一合约的分钟线数据"""
    start = time()

    cl = dbMinute[symbol]
    cl.ensure_index([('datetime', ASCENDING)], unique=True)  # 添加索引

    df = jq.get_price(setting[symbol],start_date = startDate,end_date = endDate, frequency='1m', fields=FIELDS,skip_paused = True)
    for ix, row in df.iterrows():
        bar = generateVtBar(row, symbol)
        d = bar.__dict__
        flt = {'datetime': bar.datetime}
        cl.replace_one(flt, d, True)

    end = time()
    cost = (end - start) * 1000

    print(u'合约%s的分钟K线数据下载完成%s - %s，耗时%s毫秒' % (symbol, df.index[0], df.index[-1], cost))
    print(jq.get_query_count())

def jqdownloadMappingExcel(exportpath = "C:\Project\\"):
    getfuture = jq.get_all_securities(types=['stock'], date=None)
    # list: 用来过滤securities的类型, list元素可选: ‘stock’, ‘fund’, ‘index’, ‘futures’, ‘etf’, ‘lof’, ‘fja’, ‘fjb’.types为空时返回所有股票, 不包括基金, 指数和期货
    getfuture.to_csv(
                    exportpath + "Mapping" + str(date.today())  + "index.xls",
                    index=True, header=True)


# ----------------------------------------------------------------------
def downloadAllMinuteBar(days = 1,startDate = 0,endDate = 0):
    """下载所有配置中的合约的分钟线数据"""
    print('-' * 50)
    print(u'开始下载合约分钟线数据')
    print('-' * 50)
    if days != 0:
        startDt = datetime.today() - days * timedelta(1)
        startDate = startDt.strftime('%Y-%m-%d')
        # startDate = ('2015-01-01')
        # 添加下载任务
        enddt = datetime.today()
        endDate = enddt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        startDate = startDate
        endDate = endDate


    # jqdownloadMinuteBarBySymbol('601318.XSHG', '2018-1-1', '2019-5-14')
    jqdownloadMinuteBarBySymbol('i8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('m8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('ag8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('bu8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('TA8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('MA8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('rb8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('TA8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('p8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('ru8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('SR8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('CF8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('fu8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('RM8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('c8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('pp8888', startDate, endDate)
    jqdownloadMinuteBarBySymbol('y8888', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('rb8888day', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('rb1905', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('rb1910', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('rb2001', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('m1909', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('m2001', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('ag1912', startDate, endDate)
    # jqdownloadMinuteBarBySymbol('ag2002', startDate, endDate)
    print('-' * 50)
    print
    u'合约分钟线数据下载完成'
    print('-' * 50)

if __name__ == '__main__':
    # jqdownloadMappingExcel()
    #下载主力合约

    downloadAllMinuteBar(10,0,0)
    # start = datetime.strptime("20150101", '%Y%m%d')
    # end = datetime.strptime("20161120", '%Y%m%d')
    # downloadAllMinuteBar(0,start,end)
    # jqdownloadMinuteBarBySymbol('rb1910', start, end)
    # jqdownloadMinuteBarBySymbol('rb2001', start, end)
    # #下载单个品种
    # jqdownloadMinuteBarBySymbol('510050.XSHG',startDate,endDate)
