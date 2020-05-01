# encoding: UTF-8

import json
import time
from datetime import datetime, timedelta
from typing import List

import jqdatasdk as jq
from vnpy.trader.constant import Exchange, Interval
from vnpy.trader.database import database_manager
from vnpy.trader.object import (
	BarData
)


class JQDataService:
	"""
	Service for download market data from Joinquant
	"""

	def __init__(self):
		# 加载配置
		config = open('config.json')
		self.setting = json.load(config)

		USERNAME = self.setting['jqdata.Username']
		PASSWORD = self.setting['jqdata.Password']

		try:
			jq.auth(USERNAME, PASSWORD)
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
				return f"{symbol}.XZCE"

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

	def query_history(self, symbol, exchange, start, end, interval='1m'):
		"""
		Query history bar data from JQData and update Database.
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

	def downloadAllMinuteBar(self, days=1):
		"""下载所有配置中的合约的分钟线数据"""
		if days != 0:
			startDt = datetime.today() - days * timedelta(1)
			enddt = datetime.today()
		else:
			startDt = datetime.today() - 10 * timedelta(1)
			enddt = datetime.today()

		print('-' * 50)
		print(u'开始下载合约分钟线数据')
		print('-' * 50)

		if 'Bar.Min' in self.setting:

			l = self.setting["Bar.Min"]
			for VNSymbol in l:
				dt0 = time.process_time()
				symbol = VNSymbol.split(".")[0]
				exchange = Exchange(VNSymbol.split(".")[1])
				self.query_history(symbol, exchange, startDt, enddt, interval='1m')
				cost = (time.process_time() - dt0)
				print(u'合约%s的分钟K线数据下载完成%s - %s，耗时%s秒' % (symbol, startDt, enddt, cost))
				print(jq.get_query_count())

			print('-' * 50)
			print
			u'合约分钟线数据下载完成'
			print('-' * 50)
		return None


if __name__ == '__main__':
	JQdata = JQDataService()
	JQdata.downloadAllMinuteBar(days=30)
