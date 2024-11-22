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
        

        self.remote = mysql.connector.connect(
            host = "-----",
            port = 3306,
            user = "k",
            password = "----",
            database = "----"
    )

        self.cur = self.remote.cursor()

        sql_get_kind = "select * from kind"
        self.cur.execute(sql_get_kind)
        get_kind_result = self.cur.fetchall()
        #kind_list = ['EV', 'SUV', '대형', '중형', '준중형', '소형', '경차']
        kind_list = []
        for each in get_kind_result:
            kind_list.append(each[0])

        for kind in kind_list:
            self.cbKind.addItem(kind)
        

    def gotoSignup(self):
        if self.readRFID.text() and len(self.readRFID.text()):
            self.groupBox_Total.show()
        else:
            QMessageBox.warning(self, "Error", 'ID CARD 태그 후에 회원가입하실 수 있습니다.')

    def uploadToDatabase(self):
        join_membership_sql = "insert into membership (UID, name, phone) values (%s, %s, %s);"

        self.cur.execute(join_membership_sql, (self.readRFID.text(), self.inputName.text(), self.inputPhone.text()))

        join_car_sql = "insert into car (user_id, kind_name) select user_id, NULL from membership where name like %s "

        self.cur.execute(join_car_sql,  (self.inputName.text(),))

        update_car_sql = "update car set car_num = %s where kind_name is NULL"

        self.cur.execute(update_car_sql, (self.inputCarNum.text(),))

        update_kind_sql = "update car set kind_name = %s where kind_name is NULL and exists (select 1 from kind where kind_name like %s)"

        self.cur.execute(update_kind_sql, (self.cbKind.currentText(), self.cbKind.currentText()))

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
            self.inputName.setText("")
            self.inputPhone.setText("")
            self.inputCarNum.setText("")
            self.groupBox_Total.hide()

        else:
            QMessageBox.warning(self, "Error", '모두 입력 후 진행해주세요.')

    def exitClicked(self):
        if self.remote.is_connected():
            self.remote.close()
            print("데이터베이스 연결종료")
            exit_signal.exit_application(self.main_window)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()


    sys.exit(app.exec_())