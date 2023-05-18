from PyQt5 import QtGui, QtWidgets, QtCore
from datetime import datetime, timedelta
from JQDataload import JQDataService
import sys
class DownloadManager(QtWidgets.QWidget):

    def __init__(self, parent=None):
        """"""
        super().__init__(parent)


        self.downloadData = None

        self.setWindowTitle("数据下载")
        self.downSevice = JQDataService()

        # Setting Part
        self.resize(500, 480)

        self.tab_box = QtWidgets.QTabWidget()
        self.tab_downlaod = QtWidgets.QWidget()
        self.tab_high_low_check = QtWidgets.QWidget()
        self.tab_box.addTab(self.tab_downlaod,"下载数据")
        self.tab_box.addTab(self.tab_high_low_check,"极值查询")
        self.tab_downlaodUI()
        self.tab_high_low_checkUI()

        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setGeometry(QtCore.QRect(50, 180, 591, 171))
        self.textBrowser.setObjectName("textBrowser")

        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addWidget(self.tab_box )
        left_vbox.addWidget(self.textBrowser)
        left_vbox.addStretch()
        self.setLayout(left_vbox)

        sys.stdout = EmittingStr(textWritten=self.outputWritten)
        sys.stderr = EmittingStr(textWritten=self.outputWritten)




    def tab_high_low_checkUI(self):

        self.min_max_button = QtWidgets.QPushButton("查询极值")
        self.min_max_button.setFixedHeight(self.min_max_button .sizeHint().height() * 2)
        self.min_max_button.clicked.connect(self.min_max_check)

        form = QtWidgets.QFormLayout()
        self.max_days_spin = QtWidgets.QSpinBox()
        self.max_days_spin.setRange(1,10000)
        self.max_days_spin.setValue(365)
        self.past_day_spin = QtWidgets.QSpinBox()
        self.past_day_spin.setRange(1, 10000)
        self.past_day_spin.setValue(5)
        form.addRow("回溯之前天数： ", self.max_days_spin)
        form.addRow("存在极值天数", self.past_day_spin)
        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addLayout(form)
        left_vbox.addWidget(self.min_max_button)

        left_vbox.addStretch()
        self.tab_high_low_check.setLayout(left_vbox)

    def min_max_check(self):
        max_days = self.max_days_spin.value()
        past_day = self.past_day_spin.value()
        self.downSevice.compareMaxMin(max_days, past_day)
        print(self.downSevice .compareResult)



    def tab_downlaodUI(self):
        self.class_combo = QtWidgets.QComboBox()

        self.symbol_line =  QtWidgets.QLineEdit("i8888.DCE")

        self.interval_combo = QtWidgets.QComboBox()

        self.interval_combo.addItems(["1d", "1m"])

        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=3 * 365)

        self.start_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate(
                start_dt.year,
                start_dt.month,
                start_dt.day
            )
        )
        self.end_date_edit = QtWidgets.QDateEdit(
            QtCore.QDate.currentDate()
        )


        downloading_button = QtWidgets.QPushButton("下载数据")
        downloading_button.setFixedHeight(downloading_button.sizeHint().height() * 2)
        downloading_button.clicked.connect(self.download)

        self.export_button = QtWidgets.QPushButton("导出数据")
        self.export_button.setFixedHeight(downloading_button.sizeHint().height() * 2)
        self.export_button.clicked.connect(self.save_csv_more)
        self.export_button.setEnabled(False)



        form = QtWidgets.QFormLayout()
        form.addRow("K线周期", self.interval_combo)
        form.addRow("开始日期", self.start_date_edit)
        form.addRow("结束日期", self.end_date_edit)
        form.addRow("本地代码", self.symbol_line)


        left_vbox = QtWidgets.QVBoxLayout()
        left_vbox.addLayout(form)
        left_vbox.addWidget(downloading_button)
        left_vbox.addWidget(self.export_button)
        # left_vbox.addWidget(self.textBrowser)
        left_vbox.addStretch()


        # Layout
        self.tab_downlaod.setLayout(left_vbox)




    def outputWritten(self, text):
        cursor = self.textBrowser.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textBrowser.setTextCursor(cursor)
        self.textBrowser.ensureCursorVisible()

    def download(self):
        vt_symbol = self.symbol_line.text()
        interval = self.interval_combo.currentText()
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()

        start = datetime(
        	start_date.year(),
        	start_date.month(),
        	start_date.day(),
        )

        end = datetime(
        	end_date.year(),
        	end_date.month(),
        	end_date.day(),
        	23,
        	59,
        	59,
        )

        self.downloadData = self.downSevice.downloadSymbol(vt_symbol,start,end,interval)
        self.export_button.setEnabled(True)

    def save_csv_more(self):

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "保存数据", "", "xlsx(*.xlsx)")
        # path = "C:\\Users\\i333248\\OneDrive - SAP SE\\Desktop\\Downloads\\abx.xlsx"
        if not path:
            return
        # resultdata.to_excel(path)
        with open(path, "w", encoding='utf-8-sig') as f:
            self.downloadData.to_excel(path)
        QtWidgets.QMessageBox.about(self, "标题", "导出完成")

class EmittingStr(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))

if __name__ == '__main__':
    qapp = QtWidgets.QApplication(sys.argv)
    dl = DownloadManager()
    dl.show()
    print(u"上期所为SHFE；郑期所为CZCE；大连期交所为DCE")
    print(u"示例rb8888.SHFE, i8888.DCE")

    sys.exit(qapp.exec_())
