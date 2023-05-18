import xlsxwriter

# 创建工作簿
workbook = xlsxwriter.Workbook('test.xlsx')
# 创建表单
sh = workbook.add_worksheet('test')
fmt1 = workbook.add_format({'bold': True})
fmt2 = workbook.add_format({'bg_color': "#DDEBF7"})
# 字体加粗
fmt1.set_bold(True)
# 设置左对齐
fmt2.set_align('left')
# 数据
data = [
    ['', '姓名', '年龄'],
    ['', '张三', 50],
    ['', '李四', 30],
    ['', '王五', 40],
    ['', '赵六', 60],
    ['平均年龄', '', ]
]
sh.write_row(1,1, data[0], fmt1)
sh.write_row(2,1, data[1], fmt2)
sh.write_row(3,1, data[2], fmt2)
sh.write_row(4, 1,data[3], fmt2)
sh.write_row(5, 1,data[4], fmt2)
sh.write_row(6,1,[])
sh.write_row(7, 1,data[5], fmt1)

workbook.close()