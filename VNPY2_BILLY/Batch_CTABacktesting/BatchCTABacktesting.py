# encoding: UTF-8
import json
import traceback
from datetime import datetime, date
import pandas as pd
from pandas import DataFrame
from vnpy.app.cta_strategy.backtesting import BacktestingEngine
from vnpy.app.cta_strategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import TurtleSignalStrategy
from vnpy.app.cta_strategy.strategies.double_ma_strategy import DoubleMaStrategy

class BatchCTABackTest:
	"""
	提供批量CTA策略回测，输出结果到excel或pdf，和CTA策略批量优化，输出结果到excel或pdf，
	"""

	def __init__(self, vtSymbolconfig="vtSymbol.json", exportpath=".\\"):
		"""
		加载配置路径
		"""
		config = open(vtSymbolconfig)
		self.setting = json.load(config)
		self.exportpath = exportpath

	def addParameters(self, engine, vt_symbol: str, startDate, endDate, interval="1m", capital=1_000_000):
		"""
		从vtSymbol.json文档读取品种的交易属性，比如费率，交易每跳，比率，滑点
		"""
		if vt_symbol in self.setting:
			engine.set_parameters(
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
		return engine

	def runBatchTest(self, strategy_setting, startDate, endDate, portfolio):
		"""
		进行回测
		"""
		resultDf = DataFrame()
		dfportfolio = None
		for strategy_name, strategy_config in strategy_setting.items():
			engine = BacktestingEngine()
			vt_symbol = strategy_config["vt_symbol"]
			engine = self.addParameters(engine, vt_symbol, startDate, endDate)
			if type(strategy_config["setting"]) is str:
				print(strategy_config["setting"])
				engine.add_strategy(
					eval(strategy_config["class_name"]),
					json.loads(strategy_config["setting"], )
				)
			else:
				engine.add_strategy(
					eval(strategy_config["class_name"]),
					strategy_config["setting"]
				)
			engine.load_data()
			engine.run_backtesting()
			df = engine.calculate_result()
			if portfolio == True:
				if dfportfolio is None:
					dfportfolio = df
				else:
					dfportfolio = dfportfolio + df
			resultDict = engine.calculate_statistics(df, False)
			resultDict["class_name"] = strategy_config["class_name"]
			resultDict["setting"] = strategy_config["setting"]
			resultDict["vt_symbol"] = strategy_config["vt_symbol"]
			resultDf = resultDf.append(resultDict, ignore_index=True)

		if portfolio == True:
			# dfportfolio = dfportfolio.dropna()
			engine = BacktestingEngine()
			engine.calculate_statistics(dfportfolio)
			engine.show_chart(dfportfolio)
		return resultDf

	def runBatchTestJson(self, jsonpath="ctaStrategy.json", startDate=datetime(2019, 7, 1),
	                     endDate=datetime(2020, 1, 1), exporpath=None, portfolio=True):
		"""
		从ctaStrategy.json去读交易策略和参数，进行回测
		"""
		with open(jsonpath, mode="r", encoding="UTF-8") as f:
			strategy_setting = json.load(f)
		resultDf = self.runBatchTest(strategy_setting, startDate, endDate, portfolio)
		self.ResultExcel(resultDf, exporpath)
		return strategy_setting

	def runBatchTestExcecl(self, path="ctaStrategy.xls", startDate=datetime(2019, 7, 1),
	                       endDate=datetime(2020, 1, 1), exporpath=None, portfolio=False):
		"""
		从ctaStrategy.excel去读交易策略和参数，进行回测
		"""
		df = pd.read_excel(path)
		strategy_setting = df.to_dict(orient='index')
		resultDf = self.runBatchTest(strategy_setting, startDate, endDate, portfolio)
		self.ResultExcel(resultDf, exporpath)
		return strategy_setting

	def ResultExcel(self, result, export=None):
		"""
		输出交易结果到excel
		"""
		if export != None:
			exportpath = export
		else:
			exportpath = self.exportpath
		try:
			path = exportpath + "CTABatch" + str(date.today()) + "v0.xls"
			result.to_excel(path, index=False)
			print("CTA Batch result is export to %s" % path)
		except:
			print(traceback.format_exc())

		return None


if __name__ == '__main__':
	bts = BatchCTABackTest()
	bts.runBatchTestJson()
