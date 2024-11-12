import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import mysql.connector
from datetime import datetime


from_class = uic.loadUiType("main.ui")[0]


class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.Name
        self.Phone
        self.Location
        self.carNum
        self.entryLabel.hide()
        
        self.entryLog.hide()
        
        self.showCharge.hide()
        self.feeLabel.hide()
        self.Fee.hide()
        self.entryLog.setButtonSymbols(QDateTimeEdit.NoButtons)
        

        self.showCharge.clicked.connect(self.Charge)
        self.one.clicked.connect(lambda: self.getInfo(1))
        self.two.clicked.connect(lambda: self.getInfo(2))
        self.three.clicked.connect(lambda: self.getInfo(3))
        self.four.clicked.connect(lambda: self.getInfo(4))
        self.btnExit.clicked.connect(self.Exit)

        self.remote = mysql.connector.connect(
            host = "msdb.cvyy46quatrs.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "root",
            password = "Dbsalstjq128!",
            database = "iot"
        )
        self.cur = self.remote.cursor()


    def Charge(self):
        self.Fee.show()
        self.feeLabel.show()
        self.Fee.setText("")

        sql = "select p.entry_log, m.kind from parklog p join membership m on p.id = m.id where p.name like '%"+self.Name.text()+"'"

        dt_now = datetime.now()

        self.cur.execute(sql)
        
        dt_entry, kind = self.cur.fetchall()[0]
        
        match kind:
            case "EV":
                fee = 75
            case "경차":
                fee = 50
            case default:
                fee =100
        
        dt_result = (dt_now-dt_entry).seconds * fee
        
        self.Fee.setText(str(dt_result)+"원")

        

    def getInfo(self, num):
        self.Fee.setText("")
        self.showCharge.show()
        self.entryLabel.show()
        self.entryLog.show()
        sql = "select name, phone, car_num, location, entry_log from parklog where location = " + str(num)
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.btnClicked(result)


    def btnClicked(self, info):
        self.Name.setText(info[0][0])
        self.Phone.setText(info[0][1])
        self.carNum.setText(info[0][2])
        self.Location.setText(info[0][3])
        dt_entry = info[0][4]
        dt_entry = QDateTime(dt_entry.year, dt_entry.month, dt_entry.day, dt_entry.hour, dt_entry.minute, dt_entry.second)
        self.entryLog.setDateTime(dt_entry)
        
        #dt_exit = info[0][5]


        # if dt_exit is None:
        #     self.showCharge.hide()
        #     self.Fee.hide()
        #     self.feeLabel.hide()
        # else:
        #     self.showCharge.show()
        
        # try:
        #     dt_exit = QDateTime(dt_exit.year, dt_exit.month, dt_exit.day, dt_exit.hour, dt_exit.minute, dt_exit.second)
        #     self.exitLabel.show()
        #     self.exitLog.show()
        #     self.exitLog.setDateTime(dt_exit)
        #     self.feeLabel.show()
        #     self.Fee.show()
        # except:
        #     self.exitLabel.hide()
        #     self.exitLog.hide()
    

    def Exit(self):
        if self.remote.is_connected():
            self.remote.close()
            print("데이터베이스 연결종료")
            
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())