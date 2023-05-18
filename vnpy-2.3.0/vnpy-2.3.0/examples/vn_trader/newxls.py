xlsx_list = [["AA", 2019],
            ["FF", 2018],
            ["KK", 2019],
            ["CC", 2020],
            ["BB", 2017],
            ["GG", 2018],
            ["DD", 2019],
            ["EE", 2018]]

from openpyxl import Workbook

workbook = Workbook()
save_file = "写入文件.xls"
worksheet = workbook.active
#每个workbook创建后，默认会存在一个worksheet，对默认的worksheet进行重命名
worksheet.title = "Sheet1"
for row in xlsx_list:
    worksheet.append(row) # 把每一行append到worksheet中
    worksheet.append([" "])
workbook.save(filename=save_file) #不能忘