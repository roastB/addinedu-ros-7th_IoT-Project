import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import mysql.connector
from datetime import datetime


Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")

class WindowClass(QtBaseClass, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # setSizeGripEnabled 추가
        self.setSizeGripEnabled(True)  # 크기 조절 가능하도록 설정

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

        # [1] ParkingGuide_Line
        self.pixmap = QPixmap(self.ParkingGuideBoard.width(), self.ParkingGuideBoard.height())
        self.pixmap.fill(Qt.transparent)
        self.ParkingGuideBoard.setPixmap(self.pixmap)
        self.PathDisplay()

        # [2] ParkingGuide_LED
        self.scene = QGraphicsScene()
        
        # 적절한 위치 및 크기로 설정
        self.GuideLED_1.setScene(self.scene)
        self.GuideLED_1.setGeometry(344, 800, 50, 50)

        # 원형 LED 생성
        self.led_item = QGraphicsEllipseItem(0, 0, 20, 20)
        self.led_item.setBrush(QBrush(QColor('white')))
        self.led_item.setPen(QPen(Qt.NoPen))  # 테두리 없는 원
        
        # LED 아이템을 scene에 추가
        self.scene.addItem(self.led_item)
        self.led_on = False

    # [2] ParkingGuide_LED
    def toggle_led(self):
        if self.led_on:
            self.led_item.setBrush(QBrush(QColor('white')))  # LED OFF 상태
        else:
            self.led_item.setBrush(QBrush(QColor('red')))  # LED ON 상태
        
        self.led_on = not self.led_on

    # [1] ParkingGuideLine
    def PathDisplay(self):
        painter = QPainter(self.ParkingGuideBoard.pixmap())

        # Pen 설정
        pen1 = QPen(Qt.red, 5, Qt.SolidLine)
        pen2 = QPen(Qt.blue, 5, Qt.SolidLine)
        pen3 = QPen(Qt.green, 5, Qt.SolidLine)
        pen4 = QPen(Qt.yellow, 5, Qt.SolidLine)

        # 1번 자리
        painter.setPen(pen1)
        painter.drawLine(215, 800, 215, 50)
        painter.drawLine(215, 50, 15, 50)

        # 2번 자리
        painter.setPen(pen2)
        painter.drawLine(230, 800, 230, 50)
        painter.drawLine(230, 50, 415, 50)

        # 3번 자리
        painter.setPen(pen3)
        painter.drawLine(200, 800, 200, 350)
        painter.drawLine(200, 350, 15, 350)

        # 4번 자리
        painter.setPen(pen4)
        painter.drawLine(245, 800, 245, 350)
        painter.drawLine(245, 350, 415, 350)

        painter.end()
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
                fee = 10
            case "경차":
                fee = 5
            case default:
                fee = 20
        
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

    timer = QTimer()
    timer.timeout.connect(myWindows.toggle_led)
    timer.start(5000)  # 1초마다 ON/OFF 토글

    sys.exit(app.exec_())