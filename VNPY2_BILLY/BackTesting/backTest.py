from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import (
    AtrRsiStrategy
)
from vnpy.app.cta_strategy.strategies.one_MA_MACD_bar_strategy import OneMAMACDBarStrategy
from datetime import datetime
if __name__ == '__main__':
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol="rb8888.SHFE",
        interval="1m",
        start=datetime(2022,3, 10),
        end=datetime(2022, 9, 6),
        rate=3/10000,
        slippage=1,
        size=10,
        pricetick=1,
        capital=1_000_000,
    )
    engine.add_strategy(OneMAMACDBarStrategy,'3-2' ,{})

    engine.load_data()
    engine.run_backtesting()
    engine.calculate_result()
    engine.calculate_statistics()
    engine.show_chart()