# 1. 导入unittest
import unittest


# 2. 创建类继承unittest.TestCase
class Test(unittest.TestCase):
    # 3. 创建测试用例方法, 方法要以test开头
    # 执行顺序是根据case序号来的, 并非代码的顺序
    def test_add_01(self):
        print(3+2)

    def test_add_02(self):
        print(10+5)

if __name__ == '__main__':
    suite = unittest.TestSuite()  # 实例化TestSuite
    suite.addTest(Test("test_add_02"))  # 添加测试用例
    suite.addTest(Test("test_add_01"))
    runner = unittest.TextTestRunner()  # 实例化TextTestRunner
    runner.run(suite)  # 传入suite并执行测试用例