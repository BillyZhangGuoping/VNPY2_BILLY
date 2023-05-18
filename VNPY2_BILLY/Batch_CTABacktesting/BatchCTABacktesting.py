# encoding: UTF-8
import json
import traceback
from datetime import datetime, date
import pandas as pd
from pandas import DataFrame
from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
# 策略类是用字符串格式记录的，然后用eval方法关联类，所以必须引用，虽然编辑器提示未使用
from vnpy.app.cta_strategy.strategies.boll_channel_strategy import BollChannelStrategy
from vnpy.app.cta_strategy.strategies.king_keltner_strategy import KingKeltnerStrategy
from vnpy.app.cta_strategy.strategies.turtle_signal_strategy import TurtleSignalStrategy
from vnpy.app.cta_strategy.strategies.double_ma_strategy import DoubleMaStrategy
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import (
    AtrRsiStrategy,
)
class BatchCTABackTest:
	"""
	提供批量CTA策略回测，输出结果到excel或pdf，和CTA策略批量优化，输出结果到excel或pdf，
	"""

	def __init__(self, vtSymbolconfig="vtSymbol.json", exportpath="C:\\Users\\i333248\\OneDrive\\Documents\\OPNEW\\"):
		"""
		加载配置路径
		"""
		config = open(vtSymbolconfig)
		self.setting = json.load(config)
		self.exportpath = exportpath
		self.engine =BacktestingEngine()

	def addParameters(self, engine, vt_symbol: str, startDate, endDate, interval="1m", capital=1000000):
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
			self.engine.clear_data()
			vt_symbol = strategy_config["vt_symbol"]
			self.engine = self.addParameters(self.engine, vt_symbol, startDate, endDate)
			if type(strategy_config["setting"]) is str:
				print(strategy_config["setting"])
				self.engine.add_strategy(
					eval(strategy_config["class_name"]),
					# json.loads(strategy_config["setting"])
					eval(strategy_config["setting"])
				)
			else:
				self.engine.add_strategy(
					eval(strategy_config["class_name"]),
					strategy_config["setting"]
				)
			self.engine.load_data()
			self.engine.run_backtesting()
			df = self.engine.calculate_result()
			if portfolio == True:
				if dfportfolio is None:
					dfportfolio = df
				else:
					dfportfolio = dfportfolio + df
			resultDict = self.engine.calculate_statistics(df, False)
			resultDict["0strategy_name"] = strategy_name
			resultDict["1class_name"] = strategy_config["class_name"]
			resultDict["3setting"] = strategy_config["setting"]
			resultDict["2vt_symbol"] = strategy_config["vt_symbol"]
			resultDf = resultDf.append(resultDict, ignore_index=True)

		if portfolio == True:
			# dfportfolio = dfportfolio.dropna()
			self.engine = BacktestingEngine()
			self.engine.calculate_statistics(dfportfolio)
			self.engine.show_chart(dfportfolio)

		return resultDf

	def runBatchTestJson(self, jsonpath="ctaStrategy.json", startDate=datetime(2021, 3, 1),
	                     endDate=datetime(2021, 9, 1), exporpath=None, portfolio=False):
		"""
		从ctaStrategy.json去读交易策略和参数，进行回测
		"""
		with open(jsonpath, mode="r", encoding="UTF-8") as f:
			strategy_setting = json.load(f)
		resultDf = self.runBatchTest(strategy_setting, startDate, endDate, portfolio)
		self.ResultExcel(resultDf, exporpath)
		return strategy_setting

	def runBatchOptimationJson(self,jsonpath = 'Optimization.json', OpApproach = "GA",target ="sharpe_ratio",startDate=datetime(2021, 3, 1), endDate=datetime(2021, 9, 1) ,exporpath=None):
		with open(jsonpath, mode="r", encoding="UTF-8") as f:
			Optimze_setting_list = json.load(f)
		for optimaztionName, optimzation_Setting in Optimze_setting_list.items():
			result = self.Optimize(optimzation_Setting,OpApproach,target,startDate, endDate)
			optimaztionNameTest = optimzation_Setting["class_name"] + "_" + "vt_symbol"
			self.ResultExcel(result,optimaztionNameTest,exporpath)



	def Optimize(self,optimzation_Setting, OpApproach = "GA",target ="sharpe_ratio",startDate=datetime(2021, 3, 1), endDate=datetime(2021, 9, 1)):
		self.engine.clear_data()
		vt_symbol = optimzation_Setting["vt_symbol"]
		opimization_setting = optimzation_Setting["setting"]
		self.engine = self.addParameters(self.engine, vt_symbol, startDate, endDate)
		self.engine.add_strategy(eval(optimzation_Setting["class_name"]),{})
		setting = OptimizationSetting()
		setting.set_target(target)
		for key, params in opimization_setting.items():
			setting.add_parameter(key, params[0], params[1], params[2])
		if OpApproach == "GA":
			result = self.engine.run_ga_optimization(setting)
		else:
			result = self.engine.run_bf_optimization(setting)

		return result



	def runBatchTestExcecl(self, path="ctaStrategy.xls", startDate=datetime(2020, 1, 1),
	                       endDate=datetime(2021, 9, 1), exporpath=None, portfolio=False):
		"""
		从ctaStrategy.excel去读交易策略和参数，进行回测
		"""
		df = pd.read_excel(path)
		strategy_setting = df.to_dict(orient='index')
		resultDf = self.runBatchTest(strategy_setting, startDate, endDate, portfolio)
		exporname = "BatchTestExcel"
		self.ResultExcel(resultDf, exporname, exporpath)
		return strategy_setting

	def ResultExcel(self, result, exportfileName = "CTABatch",export=None):
		"""
		输出交易结果到excel
		"""
		if export != None:
			exportpath = export
		else:
			exportpath = self.exportpath
		try:
			path = exportpath + exportfileName + str(date.today()) + "v02.xls"
			if isinstance(result,list):
				resultdf = DataFrame()
				className = exportfileName.split("_")[0]
				symbol= exportfileName.split("_")[1]
				for resultItem in result:
					itemDict = {}
					itemDict["class_name"] = className
					itemDict["symbol"] = symbol
					itemDict["Setting"] = resultItem[0]
					itemDict["Target"] = resultItem[1]
					itemDict.update(resultItem[2])
					resultdf = resultdf.append(itemDict, ignore_index=True)
			else:
				resultdf = result

			resultdf.to_excel(path, index=False)
			print("CTA Batch result is export to %s" % path)
		except:
			print(traceback.format_exc())

		return None

	def runSingleBackTesting(self,vt_symbol,class_name,strategy_setting, startDate=datetime(2020, 1, 1),
	                       endDate=datetime(2021, 8, 1),showGraph = True):
		self.engine = self.addParameters(self.engine, vt_symbol, startDate, endDate)
		self.engine.clear_data()
		self.engine.add_strategy(class_name,strategy_setting)
		self.engine.load_data()
		self.engine.run_backtesting()
		self.engine.calculate_result()
		self.engine.calculate_statistics()

		if showGraph == True:
			self.engine.show_chart()


if __name__ == '__main__':
	starttime = datetime.now()

	bts = BatchCTABackTest()
	bts.runSingleBackTesting("MA8888.CZCE",AtrRsiStrategy,
	                         {'atr_length': 10, 'atr_ma_length': 10, 'rsi_length': 30, 'rsi_entry': 20,
	                          'trailing_percent': 1.0}

	                         )



