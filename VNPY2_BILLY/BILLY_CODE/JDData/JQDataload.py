# encoding: UTF-8

from __future__ import print_function
import json
from datetime import datetime,date,timedelta
from time import time

from pymongo import MongoClient, ASCENDING

from vnpy.trader.constant import Exchange, Interval
from typing import List
from vnpy.trader.object import (
    BarData
)
from vnpy.trader.database import database_manager
import jqdatasdk as jq



class JQDataService:
    """
    Service for download market data from Joinquant
    """
    def __init__(self):
        # 加载配置
        config = open('config.json')
        setting = json.load(config)

        USERNAME = setting['jqdata.Username']
        PASSWORD = setting['jqdata.Password']

        try:
            jq.auth(USERNAME,PASSWORD)
        except Exception as ex:
            print("jq auth fail:" + repr(ex))

    def to_jq_symbol(self, symbol: str, exchange: Exchange):
        """
        CZCE product of RQData has symbol like "TA1905" while
        vt symbol is "TA905.CZCE" so need to add "1" in symbol.
        """
        if exchange in [Exchange.SSE, Exchange.SZSE]:
            if exchange == Exchange.SSE:
                jq_symbol = f"{symbol}.XSHG"  # 上海证券交易所
            else:
                jq_symbol = f"{symbol}.XSHE"  # 深圳证券交易所
        elif exchange == Exchange.SHFE:
            jq_symbol = f"{symbol}.XSGE"  # 上期所
        elif exchange == Exchange.CFFEX:
            jq_symbol = f"{symbol}.CCFX"  # 中金所
        elif exchange == Exchange.DCE:
            jq_symbol = f"{symbol}.XDCE"  # 大商所
        elif exchange == Exchange.INE:
            jq_symbol = f"{symbol}.XINE"  # 上海国际能源期货交易所
        elif exchange == Exchange.CZCE:
            # 郑商所 的合约代码年份只有三位 需要特殊处理
            for count, word in enumerate(symbol):
                if word.isdigit():
                    break

            # Check for index symbol
            time_str = symbol[count:]
            if time_str in ["88", "888", "99", "8888"]:
                return symbol

            # noinspection PyUnboundLocalVariable
            product = symbol[:count]
            year = symbol[count]
            month = symbol[count + 1:]

            if year == "9":
                year = "1" + year
            else:
                year = "2" + year

            jq_symbol = f"{product}{year}{month}.XZCE"

        return jq_symbol.upper()

    def query_history(self, symbol,exchange, start, end,interval = '1m'):
        """
        Query history bar data from JQData.
        """

        jq_symbol = self.to_jq_symbol(symbol, exchange)
        # if jq_symbol not in self.symbols:
        #     return None

        # For querying night trading period data
        # end += timedelta(1)
        now = datetime.now()
        if end >= now:
            end = now
        elif end.year == now.year and end.month == now.month and end.day == now.day:
            end = now

        df = jq.get_price(
            jq_symbol,
            frequency=interval,
            fields=["open", "high", "low", "close", "volume"],
            start_date=start,
            end_date=end,
            skip_paused=True
        )

        data: List[BarData] = []

        if df is not None:
            for ix, row in df.iterrows():
                bar = BarData(
                    symbol=symbol,
                    exchange=exchange,
                    interval=Interval.MINUTE,
                    datetime=row.name.to_pydatetime() - timedelta(minutes=1),
                    open_price=row["open"],
                    high_price=row["high"],
                    low_price=row["low"],
                    close_price=row["close"],
                    volume=row["volume"],
                    gateway_name="JQ"
                )
                data.append(bar)
        database_manager.save_bar_data(data)

        return data



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

    JQdata = JQDataService()
    # jqdownloadMinuteBarBySymbol('601318.XSHG', '2018-1-1', '2019-5-14')
    JQdata.query_history('rb8888',Exchange.SHFE, startDt, enddt,)
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
    downloadAllMinuteBar(days = 30)