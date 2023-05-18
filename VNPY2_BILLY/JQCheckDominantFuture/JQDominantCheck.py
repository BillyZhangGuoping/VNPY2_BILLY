# encoding: UTF-8
import json
from datetime import datetime, timedelta
import logging
import jqdatasdk as jq
import os

class JQDominantCheck:
	"""
	Service for download market data from Joinquant
	"""

	def __init__(self):
		# 加载配置
		configfile = "C:\\Users\\i333248\\.vntrader\\ZhuLiQieHuan\\JQDominantConfig.json"
		config = open(configfile,encoding='utf-8')
		self.setting = json.load(config)

		USERNAME = self.setting['jqdata.Username']
		PASSWORD = self.setting['jqdata.Password']
		self.check_days = self.setting["check_days"]
		self.check_symbol_dict = self.setting['symbol_list']
		self.filename = "C:\\Users\\i333248\\.vntrader\\ZhuLiQieHuan\\zhuliheyueqiehuan.log"

		if self.check_days < 1:
			self.check_days = 1
		self.dominant_change = False
		self.logger = self.define_logger()

		try:
			jq.auth(USERNAME, PASSWORD)
		except Exception as ex:
			print("jq auth fail:" + repr(ex))

	def check_dominant(self,symbol,startdate,enddate) -> str:
		"""
		传入合约名，返回str
		:param symbol:
		:return:
		"""
		dominant_symbol_list = jq.get_dominant_future(symbol.upper(),startdate,enddate)

		if dominant_symbol_list is not None:
			last_symbol_series = dominant_symbol_list.tail(self.check_days+1).drop_duplicates()
			if len(last_symbol_series)>1:
				self.dominant_change =True
				strLen = f"请注意在{list(last_symbol_series.index)[-1]}日，{symbol} {self.check_symbol_dict.get(symbol).get('name')}主力合约切换: {self.to_vq_symbol(last_symbol_series[-2])} -> {self.to_vq_symbol(last_symbol_series[-1])}. "
				self.logger.info(strLen)
		else:
			self.logger.info("主力合约无法确定，检查合约代码")


	def define_logger(self):
		logger = logging.getLogger('check_dominant')
		logger.setLevel(level=logging.INFO)
		formatter = logging.Formatter('[%(asctime)s] %(message)s')

		file_handler = logging.FileHandler(
			self.filename, mode="a", encoding="utf8"
		)
		file_handler.setFormatter(formatter)

		stream_handler = logging.StreamHandler()
		stream_handler.setFormatter(formatter)
		logger.addHandler(file_handler)
		logger.addHandler(stream_handler)
		return logger

	def query_dominant_symbols(self):
		"""
		Query history bar data from JQData and update Database.
		"""

		startdate = datetime.now() - timedelta(days=self.check_days + 10)
		endDate = datetime.now()
		symbol_list = self.check_symbol_dict.keys()
		for symbol in symbol_list:
			self.check_dominant(symbol, startdate, endDate)
		if self.dominant_change == True:
			os.startfile(self.filename)

	def to_vq_symbol(self, symbol_exchange):
		"""
		CZCE product of RQData has symbol like "TA1905" while
		vt symbol is "TA905.CZCE" so need to add "1" in symbol.
		"""
		symbol,exchange = symbol_exchange.split(".")
		if exchange in ["XSHG", "XSHE"]:
			if exchange == "XSHG":
				vt_symbol = f"{symbol}.SSE"  # 上海证券交易所
			else:
				vt_symbol = f"{symbol}.SZSE"  # 深圳证券交易所
		elif exchange == "XSGE":
			vt_symbol = f"{symbol.lower()}.SHFE"  # 上期所
		elif exchange == "CCFX":
			vt_symbol = f"{symbol}.CFFEX"  # 中金所
		elif exchange == "XDCE":
			vt_symbol = f"{symbol.lower()}.DCE"  # 大商所
		elif exchange == "XINE":
			vt_symbol = f"{symbol}.INE"  # 上海国际能源期货交易所
		elif exchange == "XZCE":
			# 郑商所 的合约代码年份只有三位 需要特殊处理


			# noinspection PyUnboundLocalVariable
			count = 2
			product = symbol[:count]
			month = symbol[count + 1:]
			vt_symbol = f"{product}{month}.CZCE"

		return vt_symbol


if __name__ == '__main__':
	JQdata = JQDominantCheck()
	JQdata.query_dominant_symbols()
