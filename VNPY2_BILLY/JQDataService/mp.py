import multiprocessing as mp
from dataclasses import dataclass
from typing import Dict, List
import threading

class ShareManager:
    # 单例对象
    # _instance = None

    # def __new__(cls, *args, **kwargs):
    #     """创建对象，保证单例"""
    #     if not cls._instance:
    #         cls._instance = super(ShareManager, cls).__new__(cls, *args, **kwargs)
    #     return cls._instance

    """单例模式————最多只允许创建一个该类实例"""
    _lock = threading.Lock()
    _instance = None

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            # print("进入lock区域")
            if not cls._instance:
                cls._instance = object.__new__(cls)
                # cls._instance = super().__new__(cls)    # 与上一条作用相同
                # cls._instance.a = a
        return cls._instance



    def __init__(self):
        # 首次初始化时创建连接池
        # if not hasattr(self, 'manager'):
        self.manager = mp.Manager()
        self.data = self.manager.dict()

    def get_bar_list(self, key) -> List:
        return self.data.get(key)

    def get_keys(self) -> List:
        return list(self.data.keys())

    def get_values(self) -> List:
        return list(self.data.values())

    def get_items(self) -> List:
        return list(self.data.items())

    def exists(self, key) -> bool:
        return key in self.data.keys()

    def set_bar_list(self, key, value):
        self.data[key] = value

    def delete_data(self, key):
        if key in self.data:
            del self.data[key]

    def all_delete_data(self):
        self.data.clear()

    def close(self):
        self.manager.shutdown()

    def set_data(self,*args, **kwargs):
        for key, value in kwargs.items():
            print("{0} == {1}".format(key, value))
            self.data[key] = value
            print(self.data)

    def get_data(self,key):
        return list(self.data.items())

@dataclass
class HistoryData:
    """
    Candlestick bar data of a certain trading period.
    """

    key: str = ""
    data: list = None


# 在多进程中使用共享内存管理器
def worker(*args, **kwargs):
    sm = ShareManager()
    sm.set_data(*args, **kwargs)
    print(sm)


if __name__ == '__main__':
    p1 = mp.Process(target=worker, kwargs={"Process1":"999"})
    p2 = mp.Process(target=worker, kwargs={"Process2":22})
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    sm = ShareManager()
    print(sm.get_data("Process1"))
    print(sm.get_data("Process2"))