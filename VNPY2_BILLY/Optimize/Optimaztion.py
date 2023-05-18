from datetime import datetime
from Batch_CTABacktesting.BatchCTABacktesting import BatchCTABackTest

if __name__ == '__main__':
	starttime = datetime.now()

	bts = BatchCTABackTest()
	bts.runBatchOptimationJson("Optimization.json",OpApproach = "GA")

	endtime = datetime.now()
	print("starttime: %s | finish time:%s | cost time :%s" %(starttime,endtime, endtime-starttime))