from vnpy.app.cta_strategy.backtesting import BacktestingEngine, OptimizationSetting
from vnpy.app.cta_strategy.strategies.atr_rsi_strategy import (
    AtrRsiStrategy,
)
from datetime import datetime

engine = BacktestingEngine()
engine.set_parameters(
    vt_symbol="rb8888.SHFE",
    interval="1m",
    start=datetime(2021,3, 10),
    end=datetime(2021, 9, 6),
    rate=3/10000,
    slippage=1,
    size=10,
    pricetick=1,
    capital=1_000_000,
)
engine.add_strategy(AtrRsiStrategy, {})

setting = OptimizationSetting()
setting.set_target("sharpe_ratio")
setting.add_parameter("atr_length", 3, 39, 1)
setting.add_parameter("atr_ma_length", 10, 30, 1)

engine.run_ga_optimization(setting)