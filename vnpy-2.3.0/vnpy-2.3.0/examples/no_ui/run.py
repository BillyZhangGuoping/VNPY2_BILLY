import multiprocessing
import json
from threading import Timer
import sys
import os
from time import sleep
from datetime import datetime, time
from logging import INFO

# Chinese futures market trading period (day/night)
DAY_START = time(8, 45)
DAY_END = time(15, 0)

NIGHT_START = time(20, 45)
NIGHT_END = time(1, 30)


def check_trading_period():
    """"""
    current_time = datetime.now().time()

    trading = False
    if (
        (current_time >= DAY_START and current_time <= DAY_END)
        or (current_time >= NIGHT_START)
        or (current_time <= NIGHT_END)
    ):
        trading = True

    return trading


def run_child(account_detail):
    """
    Running in the child process.
    """

    account_name = account_detail["account_name"]
    ctp_setting = account_detail["logon_detail"]
    # 更改工作路径
    os.chdir(account_detail["workspace"])

    # 把对vntrader 包的引用放在工作路径更改后，不然工作路径更改无法生效,
    from vnpy.event import EventEngine
    from vnpy.trader.setting import SETTINGS
    from vnpy.trader.engine import MainEngine

    from vnpy.gateway.ctp import CtpGateway
    from vnpy.app.cta_strategy import CtaStrategyApp
    from vnpy.app.cta_strategy.base import EVENT_CTA_LOG

    SETTINGS["log.active"] = True
    SETTINGS["log.level"] = INFO
    SETTINGS["log.console"] = True
    from vnpy.trader.utility import TRADER_DIR, TEMP_DIR
    # 结束引用
    SETTINGS["log.file"] = True

    event_engine = EventEngine()
    main_engine = MainEngine(event_engine)
    main_engine.add_gateway(CtpGateway)
    cta_engine = main_engine.add_app(CtaStrategyApp)
    main_engine.write_log(f" 主引擎创建成功")
    main_engine.write_log(f"工作路径: {TRADER_DIR, TEMP_DIR}")

    log_engine = main_engine.get_engine("log")
    # 更新log 格式。

    event_engine.register(EVENT_CTA_LOG, log_engine.process_log_event)
    main_engine.write_log(f"注册日志事件监听")

    main_engine.connect(ctp_setting, account_detail["gateway"])
    main_engine.write_log(f"连接CTP接口")

    sleep(10)

    cta_engine.init_engine()
    main_engine.write_log(f"CTA策略初始化完成")

    def recheck_thread():
        #每个10秒检查所有策略是否初始化完成，使用Timer线程每10秒检查，
        all_strategise_inited = False
        for strategy in cta_engine.strategies.values():
            if strategy.inited == False:
                all_strategise_inited = False
                break
            all_strategise_inited = True
        if all_strategise_inited:
            main_engine.write_log(f"CTA策略全部初始化=====")
            cta_engine.start_all_strategies()
            main_engine.write_log(f"CTA策略全部启动=====")
        else:
            newTask = Timer(10, recheck_thread)
            newTask.start()

    cta_engine.init_all_strategies()
    newTask = Timer(5, recheck_thread)
    newTask.start()


    def recheck_trading_period():
        # 每隔10秒检查是否交易时段，否则退出，使用Timer线程每10秒检查，
        trading = check_trading_period()
        if not trading:
            main_engine.write_log(f"关闭子进程")
            main_engine.close()
            sys.exit(0)
        else:
            closeTask = Timer(10, recheck_trading_period)
            closeTask.start()

    closeTask = Timer(5, recheck_trading_period)
    closeTask.start()


def run_parent():
    """
    Running in the parent process.
    """
    print("启动CTA策略守护父进程")
    with open('Mutiple_Accounts_Config.json', mode="r", encoding="UTF-8") as f:
        account_detail_list = json.load(f)

    child_process_list = []
    while True:
        trading = check_trading_period()

        # Start child process in trading period
        if trading and child_process_list == []:
            print("启动子进程")

            # 同时运行account 不应该超过cpu核心数，因为vntrader 可以看成是一个持续循环，在main_engine.close之前不会退出cpu占用；
            # 等待的运行事务将一直等待
            for account_detail in account_detail_list:
                new_process = multiprocessing.Process(target=run_child, name=account_detail["account_name"], args=(account_detail,))
                new_process.start()
                child_process_list.append(new_process)

            # # 使用进程池更加方便，但是无法给进程命名去查看log 是那个account的，所以不建议
            # pool = multiprocessing.Pool(multiprocessing.cpu_count())
            # child_process_list = pool.map_async(run_child, account_detail_list)
            print("子进程启动成功")


        # 非记录时间则退出子进程
        if not trading and child_process_list:
            for process in child_process_list:
                if not process.is_alive():
                    child_process_list.remove(process)
            if child_process_list == []:
                print("子进程关闭成功")

        sleep(10)


if __name__ == "__main__":
    run_parent()
