import multiprocessing
import time
# 看进程pid 获取进程编号
import os


# 随意的函数
def f1(k):
    print("查看本次创建f1进程的pid", os.getpid())
    print("查看本次f1进程的父pid", os.getppid())
    for i in range(k):
        print("文字")
        time.sleep(1)


def f2(k, p):
    print("查看本次创建f2进程的pid", os.getpid())
    print("查看本次f2进程的父pid", os.getppid())
    for i in range(k):
        print("文字f2", p)
        time.sleep(1)


if __name__ == "__main__":
    # 创建进程类对象
    # tartget：指定的执行函数名
    # args：元组方式给指定任务传参     (传参顺序就是任务的顺序)
    # kwargs：字典方式给指定任务传参  （key是参数的名字 value是值，需要key的名字参数名字一致）
    f3 = multiprocessing.Process(target=f1, args=(3,))
    f4 = multiprocessing.Process(target=f1, kwargs={"k": 5})
    f5 = multiprocessing.Process(target=f2, args=(3, 5))
    f6 = multiprocessing.Process(target=f2, kwargs={"k": 5, "p": "f6"})
    f7 = multiprocessing.Process(target=f2, kwargs={"p": 7, "k": 5})
    f3.start()
    f4.start()
    f5.start()
    f6.start()
    f7.start()
    print("这里是主进程", os.getpid())
