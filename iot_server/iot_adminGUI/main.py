import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import mysql.connector
import time
from datetime import datetime
import exit_signal

Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")

# 요금 업데이트용 쓰레드
class Display(QThread):
    update = pyqtSignal()

    def __init__ (self, sec=0, parent=None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        while self.running == True:
            self.update.emit()
            time.sleep(1)
        
    def stop(self):
        self.running = False


class WindowClass(QtBaseClass, Ui_MainWindow):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        
        # setSizeGripEnabled 추가
        self.setSizeGripEnabled(True)  # 크기 조절 가능하도록 설정

        self.Fee.setText("")

        self.entryLog.setButtonSymbols(QDateTimeEdit.NoButtons)
        
        #주차 자리 실시간 반영 쓰레드
        self.parkcount = Display()
        self.parkcount.daemon = True
        self.parkcount.update.connect(self.activateCurrentPlace)

        #요금 정산 쓰레드
        self.renewtimer = Display()
        self.renewtimer.daemon = True
        self.renewtimer.update.connect(self.calculateCharge)

        self.one.clicked.connect(lambda: self.getInfo(1))
        self.two.clicked.connect(lambda: self.getInfo(2))
        self.three.clicked.connect(lambda: self.getInfo(3))
        self.four.clicked.connect(lambda: self.getInfo(4))
        self.btnExit.clicked.connect(self.Exit)
        self.entryLog.hide()
        self.btnClear.clicked.connect(self.Clear)

        self.one.setEnabled(False)
        self.two.setEnabled(False)
        self.three.setEnabled(False)
        self.four.setEnabled(False)

        self.parklist = {'1': False, '2':False, '3':False, '4':False}

        self.remote = mysql.connector.connect(
            host = "****",
            port = 3306,
            user = "root",
            password = "****",
            database = "****"
        )
        self.cur = self.remote.cursor()
        # 데이터베이스 커넥션 생성 시 자동 커밋을 설정합니다.
        self.startCurrentPlace()


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

### 함수 영역 ###

## 정보 조회 초기화

    def Clear(self):
        self.Name.setText("")
        self.Phone.setText("")
        self.carNum.setText("")
        self.Location.setText("")
        self.parkTime.setText("")
        self.Fee.hide()
        self.feeLabel.hide()
        self.parkTime.hide()
        self.parkTimeLabel.hide()

        
## 주차장 자리 최신화 ##
    # 데이터베이스 갱신을 위한 함수
    def connectDatabase(self):
        print("데이터베이스 연결")
        self.remote = mysql.connector.connect(
            host = "****",
            port = 3306,
            user = "root",
            password = "****",
            database = "****"
        )
        self.cur = self.remote.cursor()

    def startCurrentPlace(self):
        self.parkcount.running = True
        self.parkcount.start()

    def stopCurrentPlace(self):
        self.parkcount.running = False
        self.parkcount.stop()

    def activateCurrentPlace(self):
        self.remote.close()
        self.connectDatabase()

        sql = "select location from parklog where entry_log is not NULL and exit_log is NULL;"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.parklist = {'1': False, '2':False, '3':False, '4':False}
        
        count = 0

        for each in result:
            each = each[0]
            self.parklist[f'{each}']=True
            count += 1
        
        self.CountBox.setText(str(count))
        self.currentPlace()

    def currentPlace(self):
        print(self.parklist)

        if self.parklist['1'] == True:
            self.one.setStyleSheet("background-color: #3498db; color: black;")
            self.one.setEnabled(True)
        else:
            self.one.setStyleSheet("background-color: #939a98; color: black;")
            self.one.setEnabled(False)
        
        if self.parklist['2'] == True:
            self.two.setStyleSheet("background-color: #3498db; color: black;")
            self.two.setEnabled(True)
        else:
            self.two.setStyleSheet("background-color: #939a98; color: black;")
            self.two.setEnabled(False)
        
        if self.parklist['3'] == True:
            self.three.setStyleSheet("background-color: #3498db; color: black;")
            self.three.setEnabled(True)
        else:
            self.three.setStyleSheet("background-color: #939a98; color: black;")
            self.three.setEnabled(False)
        
        if self.parklist['4'] == True:
            self.four.setStyleSheet("background-color: #3498db; color: black;")
            self.four.setEnabled(True)
        else:
            self.four.setStyleSheet("background-color: #939a98; color: black;")
            self.four.setEnabled(False)
##

## 주차 정보 조회 및 주차 요금 최신화 ##
    def startDisplayCharge(self):
        self.renewtimer.running = True
        self.renewtimer.start()

    def stopDisplayCharge(self):
        self.renewtimer.running = False
        self.renewtimer.stop()


    def getInfo(self, num):
        self.stopDisplayCharge()
        self.Fee.setText("")
        self.Fee.show()
        self.feeLabel.show()
        self.parkTime.show()
        self.parkTimeLabel.show()
        self.entryLabel.show()
        self.entryLog.show()
        sql = "select name, phone, car_num, location, entry_log from parklog where location = " + str(num) +" and exit_log is NULL"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.showInfo(result)

    def showInfo(self, info):
        self.startDisplayCharge()
        self.Name.setText(info[0][0])
        self.Phone.setText(info[0][1])
        self.carNum.setText(info[0][2])
        self.Location.setText(info[0][3])
        dt_entry = info[0][4]
        dt_entry = QDateTime(dt_entry.year, dt_entry.month, dt_entry.day, dt_entry.hour, dt_entry.minute, dt_entry.second)
        self.entryLog.setDateTime(dt_entry)
        self.calculateCharge()
    
    
    def calculateCharge(self):
        sql = "select p.entry_log, m.kind from parklog p join membership m on p.id = m.id where p.name like '%"+self.Name.text()+"' and p.exit_log is NULL"
        # 입차시간과 차종만 가져와.

        self.cur.execute(sql)
        try:
            dt_entry, kind = self.cur.fetchall()[0]

            self.showCharge(dt_entry, kind)
        except:
            pass
        
    
    def showCharge(self, dt_entry, kind):
        dt_now = datetime.now()
        match kind:
            case "EV":
                fee = 75
            case "경차":
                fee = 50
            case default:
                fee = 100
        try:
            dt_day = (dt_now-dt_entry).days*1440  #일을 분으로 변환
        except:
            pass

        dt_time = (dt_now-dt_entry).seconds//60 - 540 #시분초를 분으로 변환

        dt_fee = (dt_day + dt_time) * fee

        print("주차시간:", dt_entry)
        print("현재시간:", dt_now)
        print("주차요금:", str(dt_fee)+"원")
        print("=====================================")
        
        self.Fee.setText(str(dt_fee)+"원")
        self.parkTime.setText(str(dt_time)+"분")
##

## 프로그램 종료 ##
    def Exit(self):
        if self.remote.is_connected():
            #print("데이터베이스 연결종료")
            self.renewtimer.running = False
            #print("요금정산 쓰레드 종료")
            self.parkcount.running = False

            self.stopCurrentPlace()
            #print("실시간 반영 종료")
            self.renewtimer.stop()
            exit_signal.exit_application(self.main_window)

##

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    timer = QTimer()
    timer.timeout.connect(myWindows.toggle_led)
    timer.start(5000)  # 1초마다 ON/OFF 토글

    sys.exit(app.exec_())