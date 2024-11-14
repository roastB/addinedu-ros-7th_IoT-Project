import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QRegExp
from PyQt5 import uic
import mysql.connector
import exit_signal

from_class = uic.loadUiType("park_user_1.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        kind_list = ['EV', 'SUV', '대형', '중형', '준중형', '소형', '경차']

        self.inputPhone.setMaxLength(11)
        self.inputPhone.setValidator(QIntValidator())
        
        regex = QRegExp("[^0-9]*")  # 숫자 이외의 모든 문자를 허용하는 정규식
        validator = QRegExpValidator(regex)
        self.inputName.setValidator(validator)

        self.readRFID.setMaxLength(13)
        self.inputCarNum.setMaxLength(9)
        self.groupBox_Total.hide()
        self.btnUID.clicked.connect(self.gotoSignup)
        self.btnJoin.clicked.connect(self.joinClicked)
        self.btnClear.clicked.connect(self.clearClicked)
        self.btnExit.clicked.connect(self.exitClicked)
        for kind in kind_list:
            self.cbKind.addItem(kind)

        self.remote = mysql.connector.connect(
            host = "msdb.cvyy46quatrs.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "root",
            password = "Dbsalstjq128!",
            database = "iot"
        )

        self.cur = self.remote.cursor()
        

    def gotoSignup(self):
        if self.readRFID.text() and len(self.readRFID.text()) == 13:
            self.groupBox_Total.show()
        else:
            QMessageBox.warning(self, "Error", 'ID CARD 태그 후에 회원가입하실 수 있습니다.')

    def uploadToDatabase(self):
       join_sql = "insert into membership (RFID, name, phone, car_num, kind) values (%s, %s, %s, %s, %s);"

       self.cur.execute(join_sql, (self.readRFID.text(), self.inputName.text(), self.inputPhone.text(), self.inputCarNum.text(), self.cbKind.currentText()))
       self.remote.commit()

    def clearClicked(self):
        retval = QMessageBox.question(self,"초기화", "입력하신 정보를 초기화하시겠습니까?" ,QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if retval == QMessageBox.Yes:
            self.inputName.clear()
            self.inputPhone.clear()
            self.inputCarNum.clear()
        else:
            pass

    def joinClicked(self):
        if self.inputName.text() and self.inputPhone.text() and self.readRFID.text() and self.inputCarNum.text() and self.cbKind.currentText():
            QMessageBox.about(self, "회원가입", '회원가입이 완료되었습니다.')
            self.uploadToDatabase()
            self.readRFID.setText("")
            self.groupBox_Total.hide()

        else:
            QMessageBox.warning(self, "Error", '모두 입력 후 진행해주세요.')

    def exitClicked(self):
        if self.remote.is_connected():
            print("데이터베이스 연결종료")
            exit_signal.exit_application(self.main_window)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()


    sys.exit(app.exec_())