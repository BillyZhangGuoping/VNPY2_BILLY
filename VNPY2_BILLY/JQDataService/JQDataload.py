# encoding: UTF-8

import json
import time
from datetime import datetime, timedelta
from typing import List

import jqdatasdk as jq
from vnpy.trader.constant import Exchange, Interval
# from vnpy.trader.database import database_manager
from vnpy.trader.object import (
	BarData
)


class JQDataService:
	"""
	Service for download market data from Joinquant
	"""

	def __init__(self):
		# 加载配置
		config = open('C:\\Users\\i333248\\OneDrive - SAP SE\\Desktop\\Downloads\\VNPY2_BILLY\\JQDataService\\JQDataConfig.json')
		self.setting = json.load(config)

		USERNAME = self.setting['jqdata.Username']
		PASSWORD = self.setting['jqdata.Password']

		self.compareResult = ""
		self.max_min_days = 0

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

	def query_history(self, symbol, exchange, start, end, interval='1m',save_base = True):
		"""
		Query history bar data from JQData and update Database.
		"""

		jq_symbol = self.to_jq_symbol(symbol, exchange)
		# if jq_symbol not in self.symbols:
		#     return None

		# For querying night trading period data
		# end += timedelta(1)
		now =  datetime.now()
		if end >= now:
			end = now
		elif end.year == now.year and end.month == now.month and end.day == now.day:
			end = now

		df = jq.get_price(
			jq_symbol,
			frequency=interval,
			fields=['open','close','low','high','volume','money'],
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

		return df

	def downloadAllMinuteBar(self, days=0,startDt = 0):
		"""下载所有配置中的合约的分钟线数据"""
		if days == 0:
			days = self.setting["days"]
		if startDt == 0:
			startDt = datetime.today() - days * timedelta(1)
			enddt = datetime.today()
		else:
			enddt = startDt + days * timedelta(1)

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
			print(u'合约数据下载完成')
			print('-' * 50)

		return

	def compareMaxMin(self,rangeday = 365, days = 3):
		self.compareResult = ""
		self.max_min_days = days
		self.downloadAllDayBar(rangeday)
		return self.compareResult




	def downloadAllDayBar(self, days=0,startDt = 0):
		"""下载所有配置中的合约的分钟线数据"""
		if days == 0:
			days = self.setting["days"]
		if startDt == 0:
			startDt = datetime.today() - days * timedelta(1)
			enddt = datetime.today()
		else:
			enddt = startDt + days * timedelta(1)

		print('-' * 50)
		print(u'开始下载日期日线数据')
		print('-' * 50)


		if 'Bar.Min' in self.setting:
			l = self.setting["Bar.Min"]
			for VNSymbol in l:
				dt0 = time.process_time()
				symbol = VNSymbol.split(".")[0]
				exchange = Exchange(VNSymbol.split(".")[1])
				df = self.query_history(symbol, exchange, startDt, enddt, interval='1d')
				self.maxminCompare(df,VNSymbol,startDt.strftime("%Y-%m-%d"),days)
				cost = (time.process_time() - dt0)
				print(u'合约%s的日K线数据下载完成%s - %s，耗时%s秒' % (symbol, startDt, enddt, cost))
				print(jq.get_query_count())
			print('-' * 50)
			print(u'合约数据下载完成')
			print('-' * 50)

		return None

	def maxminCompare(self,bar_df,VNSymbol,startDt, days):
		bar_max = bar_df["high"]
		bar_min = bar_df["low"]
		if max(bar_max) == max(bar_max.tail(self.max_min_days)):
			self.compareResult += f"{VNSymbol} : 存在从{startDt}至今的{days}天 最高价 在最近{self.max_min_days}日中.\n"
		elif min(bar_min) == min(bar_min.tail(self.max_min_days)):
			self.compareResult += f"{VNSymbol} : 存在从{startDt}至今的{days}天 最低价 在最近{self.max_min_days}日中. \n"

	def downloadSymbol(self,vt_symbol,startDt,endDt,interval):

		print('-' * 50)
		print(u'开始下载%s线数据' %(interval))
		print('-' * 50)

		dt0 = time.process_time()
		symbol = vt_symbol.split(".")[0]
		exchange = Exchange(vt_symbol.split(".")[1])
		resultdata = self.query_history(symbol, exchange, startDt, endDt, interval=interval,save_base = False)
		cost = (time.process_time() - dt0)
		print(u'合约%s的下载完成%s - %s，耗时%s秒, 条数 %s' % (symbol, startDt, endDt, cost, len(resultdata)))
		print(jq.get_query_count())
		print('-' * 50)
		print(u'合约数据下载完成')
		print('-' * 50)

		return resultdata

	def downloadtick(self,vt_symbol,startDt,endDt):

		dt0 = time.process_time()
		symbol = vt_symbol.split(".")[0]
		exchange = Exchange(vt_symbol.split(".")[1])
		jq_symbol = self.to_jq_symbol(symbol, exchange)
		df = jq.get_ticks(jq_symbol, startDt, endDt, fields = None, skip=True,df=True)
		cost = (time.process_time() - dt0)
		print(u'合约%s的下载完成%s - %s，耗时%s秒, 条数 %s' % (symbol, startDt, endDt, cost, len(df)))

		return df


	def save_csv_more(self, resultData,name = "data") -> None:
		"""
        Save table data into a csv file
        """
		# path, _ = QtWidgets.QFileDialog.getSaveFileName(
		# 	self, "保存数据", "", "xls(*.xls)")
		path = "C:\\Users\\i333248\\OneDrive - SAP SE\\Desktop\\Downloads\\" + name + ".xls"
		if not path:
			return
		# resultdata.to_excel(path)
		with open(path, "w", encoding='utf-8-sig') as f:
			resultData.to_excel(path)

if __name__ == '__main__':

	JQdata = JQDataService()
	JQdata.compareMaxMin(365,5)
	print(JQdata.compareResult)
