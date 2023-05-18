import multiprocessing
import sys
from time import sleep
from datetime import date, datetime, time
from logging import INFO

from vnpy.event import EventEngine
from vnpy.trader.setting import SETTINGS
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp, QtCore
from vnpy.JQCheckDominantFuture.JQDominantCheck import JQDominantCheck

from vnpy.gateway.ctp import CtpGateway
from vnpy.app.cta_strategy.ui.widget import CtaManager
from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.cta_strategy.base import EVENT_CTA_LOG
from threading import Timer

SETTINGS["log.active"] = True
SETTINGS["log.level"] = INFO
SETTINGS["log.console"] = True

ctp_setting = {
    "用户名": "8006700085",
    "密码": "0752Shui",
    "经纪商代码": "4500",
    "交易服务器": "121.40.137.252:41305",
    "行情服务器": "121.40.137.252:41313",
    "产品名称": "client_vntrader_1.9.2",
    "授权编码": "L1REQQ81P5Y7Q5C8"
}


# Chinese futures market trading period (day/night)
def run_child_JQDominantCheck():
    JQdatacheck = JQDominantCheck()
    JQdatacheck.query_dominant_symbols()


def check_trading_period(current_time, dayofweek):
    """"""

    trading = False


    # 改为在下面时间段停止执行vnTrade，
    closeTime_morning_start = time(8, 50)
    closeTime_morning_end = time(8, 56)
    closeTime_mid_start = time(13, 20)
    closeTime_mid_end = time(13, 26)
    closeTime_night_start = time(20, 50)
    closeTime_night_end = time(20, 56)

    if (not (
            (closeTime_morning_start <current_time < closeTime_morning_end) or
            (closeTime_mid_start < current_time < closeTime_mid_end)
            or (closeTime_night_start < current_time < closeTime_night_end)

    )) or dayofweek >= 5:
        trading = True

    return trading


def run_child():
    """
    Running in the child process.
    """
    SETTINGS["log.file"] = True
    qapp = create_qapp()

    event_engine = EventEngine()
    #  cat_event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)

    main_window = MainWindow(main_engine, event_engine)
    main_window.showMaximized()

    main_window.open_widget(CtaManager, 'CtaStrategy')

    # cta_window = main_window.widgets['CtaStrategy']
    # cta_window.show()

    def recheck_thread():
        all_strategise_inited = False
        for strategy in cta_engine.strategies.values():
            if strategy.inited == False:
                all_strategise_inited = False
                break
            all_strategise_inited = True
        if all_strategise_inited:
            main_engine.write_log("CTA策略全部初始化=====")

            cta_engine.start_all_strategies()
            # cta_engine.stop_all_strategies()
            main_engine.write_log("CTA策略全部启动=====")
        else:
            newTask = Timer(10, recheck_thread)
            newTask.start()

    def start_cta():
        main_engine.write_log("主引擎创建成功")

        log_engine = main_engine.get_engine("log")
        event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)

        main_engine.write_log("注册日志事件监听")

        main_engine.connect(ctp_setting, "CTP")
        main_engine.write_log("连接CTP接口")

        sleep(30)

        # cta_engine.init_engine()
        main_engine.write_log("CTA策略初始化开始=====")

        cta_engine.init_all_strategies()

        newTask = Timer(5, recheck_thread)
        newTask.start()

    QtCore.QTimer.singleShot(2000, start_cta)

    qapp.exec()


def run_parent():
    """
    Running in the parent process.
    """
    print("启动CTA策略守护父进程")

    child_process = None
    child_process_child_JQDominantCheck = None

    while True:
        current_time = datetime.now().time()
        dayofweek = datetime.now().weekday()
        trading = check_trading_period(current_time, dayofweek)
        # Start child process in trading period
        if trading and child_process is None:
            print("启动子进程")
            child_process = multiprocessing.Process(target=run_child)
            child_process.start()

        # 非记录时间则退出子进程
        if not trading and child_process is not None:
            print("关闭子进程")
            child_process.terminate()
            child_process = None

        if time(8, 32) >= current_time >= time(8, 21) and dayofweek < 5 and child_process_child_JQDominantCheck is None:
            print("启动主力合约查询子进程")
            child_process_child_JQDominantCheck = multiprocessing.Process(target=run_child_JQDominantCheck)
            child_process_child_JQDominantCheck.start()

        if (child_process_child_JQDominantCheck is not None) and current_time > time(8, 32):
            print("关闭主力合约查询子进程")
            child_process_child_JQDominantCheck.terminate()
            child_process_child_JQDominantCheck = None

        sleep(60)


if __name__ == "__main__":
    run_parent()