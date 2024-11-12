import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from PyQt5 import uic
import mysql.connector

from_class = uic.loadUiType("park_user_1.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self):
        print("user mode")
        super().__init__()
        self.setupUi(self)
        kind_list = ['EV', 'SUV', '대형', '중형', '준중형', '소형', '경차']

        self.inputName
        self.inputPhone
        self.inputRFID
        self.inputCarNum
        self.btnJoin.clicked.connect(self.joinClicked)
        self.btnClear.clicked.connect(self.clearClicked)
        self.btnExit.clicked.connect(self.exitClicked)
        for kind in kind_list:
            self.cbKind.addItem(kind)

        self.remote = mysql.connector.connect(
            host = "host",
            port = "port",
            user = "root",
            password = "your password",
            database = "database"
        )

        self.cur = self.remote.cursor()
        
        
    def uploadToDatabase(self):
       join_sql = "insert into membership (RFID, name, phone, car_num, kind) values (%s, %s, %s, %s, %s);"

       self.cur.execute(join_sql, (self.inputRFID.text(), self.inputName.text(), self.inputPhone.text(), self.inputCarNum.text(), self.cbKind.currentText()))
       self.remote.commit()

    def clearClicked(self):
        retval = QMessageBox.question(self,"초기화", "입력하신 정보를 초기화하시겠습니까?" ,QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if retval == QMessageBox.Yes:
            self.inputName.clear()
            self.inputPhone.clear()
            self.inputRFID.clear()
            self.inputCarNum.clear()
        else:
            pass

    def joinClicked(self):
        if self.inputName.text() and self.inputPhone.text() and self.inputRFID.text() and self.inputCarNum.text() and self.cbKind.currentText():
            QMessageBox.about(self, "회원가입", '회원가입이 완료되었습니다.')
            self.uploadToDatabase()
            self.inputName.clear()
            self.inputPhone.clear()
            self.inputRFID.clear()
            self.inputCarNum.clear()

        else:
            QMessageBox.warning(self, "Error", '모두 입력 후 진행해주세요.')

    def exitClicked(self):
        if self.remote.is_connected():
            print("mysql 종료")
            self.remote.close()

        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()


    sys.exit(app.exec_())