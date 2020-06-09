# encoding: UTF-8
import json
import traceback
from datetime import datetime, date

from pandas import DataFrame
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import AtrRsiStrategy

class BatchCTABackTest:
	"""
	提供批量CTA策略回测，输出结果到excel或pdf，和CTA策略批量优化，输出结果到excel或pdf，
	"""

	def __init__(self, vtSymbolconfig="vtSymbol.json", exportpath=".\\"):
		"""
		加载配置路径
		"""
		# TODO
		config = open(vtSymbolconfig)
		self.setting = json.load(config)
		self.engine = BacktestingEngine()
		self.resultDf = DataFrame()
		self.exportpath = exportpath

	def addParameters(self, vt_symbol: str, startDate, endDate, interval="1m", capital=1_000_000):
		"""

		"""
		# TODO
		if vt_symbol in self.setting:
			self.engine.set_parameters(
				vt_symbol=vt_symbol,
				interval=interval,
				start=startDate,
				end=endDate,
				rate=self.setting[vt_symbol]["rate"],
				slippage=self.setting[vt_symbol]["slippage"],
				size=self.setting[vt_symbol]["size"],
				pricetick=self.setting[vt_symbol]["pricetick"],
				capital=capital
			)
		else:
			print("symbol %s hasn't be maintained in config file" % vt_symbol)
		return None

	def runBatchTestJson(self, jsonpath="ctaStrategy.json", startDate=datetime(2019, 1, 1),
	                     endDate=datetime(2020, 1, 1)):
		"""
		Load setting file.
		"""

		with open(jsonpath, mode="r", encoding="UTF-8") as f:
			strategy_setting = json.load(f)

		for strategy_name, strategy_config in strategy_setting.items():
			vt_symbol = strategy_config["vt_symbol"]
			self.addParameters(vt_symbol, startDate, endDate)
			self.engine.add_strategy(
				eval(strategy_config["class_name"]),
				strategy_config["setting"]
			)
			self.engine.load_data()
			self.engine.run_backtesting()
			df = self.engine.calculate_result()
			resultDict = self.engine.calculate_statistics(df, False)
			resultDict["class_name"] = strategy_config["class_name"]
			resultDict["setting"] = strategy_config["setting"]
			self.resultDf = self.resultDf.append(resultDict, ignore_index=True)
		self.ResultExcel(self.resultDf)
		return self.resultDf

	def runBatchTestCSV(self, csvpath, expeort='Excel'):
		# TODO
		return None

	def ResultExcel(self, result):
		# TODO
		try:
			path = self.expertpath + "CTABatch" + str(date.today()) + "v0.xls"
			result.to_excel(path, index=False)

		except:
			print(traceback.format_exc())

		return None


if __name__ == '__main__':
	bts = BatchCTABackTest()
	bts.runBatchTestJson()
