import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import mysql.connector
import time
from datetime import datetime, timedelta
import exit_signal
import time
import pyqtgraph as pg
import itertools

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

        # 주차장 이미지 추가
        self.add_parking_image() 

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

        self.left_1.clicked.connect(lambda: self.getInfo('LEFT_1'))
        self.left_2.clicked.connect(lambda: self.getInfo('LEFT_2'))
        self.right_1.clicked.connect(lambda: self.getInfo('RIGHT_1'))
        self.right_2.clicked.connect(lambda: self.getInfo('RIGHT_2'))
        self.btnExit.clicked.connect(self.Exit)
        self.entryLog.hide()
        self.btnClear.clicked.connect(self.Clear)

        self.left_1.setEnabled(False)
        self.left_2.setEnabled(False)
        self.right_1.setEnabled(False)
        self.right_2.setEnabled(False)

        self.parklist = {'LEFT_1': False, 'LEFT_2':False, 'RIGHT_1':False, 'RIGHT_2':False}

        self.remote = mysql.connector.connect(
            host = "msdb.cvyy46quatrs.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "root",
            password = "Dbsalstjq128!",
            database = "iot"
        )
        self.cur = self.remote.cursor()

        # 데이터베이스 커넥션 생성 시 자동 커밋을 설정합니다.
        self.startCurrentPlace()

        #############################################################################
        #############################################################################
        self.SalesGraph = self.findChild(QWidget, "graphicsView_2")

        if self.SalesGraph is not None:
            black_layout = QVBoxLayout(self.SalesGraph)  # black_layout이라는 QVBoxLayout을 SalesGraph 위젯에 설정
            self.SalesGraph.setLayout(black_layout)  # SalesGraph 위젯에 레이아웃 설정

            # 첫 번째 그래프에 표시할 데이터
            x = [1, 3, 5, 7, 9, 11]     # x:날짜
            y = [4, 7, 10, 49, 50, 45]  # y:금일매출, 주차한 차량 수 등등
            # 두 번째 그래프에 표시할 데이터
            x2 = [2, 4, 6, 8, 10]     # x: 다른 데이터 (예: 주차된 차량 수)
            y2 = [1, 3, 7, 25, 30]    # y: 또 다른 데이터 (예: 주차된 차량의 수 변화)

            self.Graph_1 = pg.PlotWidget(self)
            black_layout.addWidget(self.Graph_1) 

            self.Graph_2 = pg.PlotWidget(self)
            black_layout.addWidget(self.Graph_2)

            self.Graph_1.plot(
                x,
                y,  # 데이터 값
                title='Plot test',  # 그래프의 제목
                pen='r',  # 그래프 선의 색을 빨간색으로 설정
                symbol='o',  # 데이터 점을 원형('o')으로 표시
                symbolPen='g',  # 데이터 점의 외곽선 색을 초록색('g')으로 설정
                symbolBrush=0.3  # 데이터 점의 채우기 색의 투명도 설정 (0.2는 낮은 투명도)
            )
            self.Graph_1.showGrid(x=True, y=True)  
            self.Graph_1.setTitle('매출 통계')

            self.Graph_2.plot(
                x2,
                y2,  # 데이터 값
                title='Plot test 2',  # 그래프의 제목
                pen='b',  # 그래프 선의 색을 파란색으로 설정
                symbol='x',  # 데이터 점을 'x'로 표시
                symbolPen='y',  # 데이터 점의 외곽선 색을 노란색으로 설정
                symbolBrush=0.3  # 데이터 점의 채우기 색의 투명도 설정 (0.4는 더 높은 투명도)
            )
            self.Graph_2.showGrid(x=True, y=True)  
            self.Graph_2.setTitle('주차된 차량 수')
        else:
            print("SalesGraph:graphicsView_2 위젯을 찾을 수 없습니다.")

        #############################################################################
        #############################################################################
    
        ###################################################################
        ## 주차중인 차량 갯수와 자리에 따라 LED 제어 : [1] LED 몇개 켜야하는지 판단! ##
        ###################################################################

        # 각 라디오 버튼에 대한 독립적인 타이머 생성
        self.timer = QTimer(self)
    
        self.repeat = [ i for i in range(1, 17)]

        # 현재까지 주차중인 갯수 및 자리 찾는 쿼리문(Still Parking)
        stillParking_sql = "SELECT p.id, p.name, p.location, p.exit_log FROM membership m, parklog p WHERE m.id = p.id AND p.location not LIKE 'NY' AND p.exit_log is NULL;"
        self.cur.execute(stillParking_sql)
        stillP_result = self.cur.fetchall()
        stillP_len = len(stillP_result)

        # [1] LED 몇개 켜야하는지 판단!
        if stillP_len == 0: # 모두 비워져있음.
            self.timer.timeout.connect(self.blink_led_ALL)
            
        elif stillP_len == 1:  # 1곳이 주차 중 (3곳이 가능)
            isParking_1 = stillP_result[0][2]
            self.timer.timeout.connect(lambda: self.blink_led_THREE(isParking_1))

        elif stillP_len == 2:  # 2곳이 주차 중 (2곳이 가능)
            isParking_2 = [stillP_result[i][2] for i in range(2)]
            self.timer.timeout.connect(lambda: self.blink_led_TWO(isParking_2))
        
        elif stillP_len == 3:  # 3곳이 주차 중 (1곳이 가능)
            isParking_3 = [stillP_result[i][2] for i in range(3)]
            self.timer.timeout.connect(lambda: self.blink_led_ONE(isParking_3))

        else:
            print("죄송합니다. 현재는 만차입니다. 주차할 곳이 없습니다.")

        self.timer.start(1000)


###############
### 함수 영역 ###
###############

    ##########################################################
    ## 주차중인 차량 갯수와 자리에 따라 LED 제어 : [2] LED ON 함수  ##
    ##########################################################
    
    def blink_led_ALL(self):
        for i in range(1, 17):
            radio_button = getattr(self, f"radioButton_{i}")
            self.Bright_LED(radio_button)

    def blink_led_THREE(self, isParking_1):
        if isParking_1 == "LEFT_1":
            self.repeat = [x for x in self.repeat if x not in [9, 10]]
    
        elif isParking_1 == "LEFT_2":
            self.repeat = [x for x in self.repeat if x not in [13, 14]]
    
        elif isParking_1 == "RIGHT_1":
            self.repeat = [x for x in self.repeat if x not in [11, 12]]
    
        else:   # RIGHT_2
            self.repeat = [x for x in self.repeat if x not in [15, 16]]
    
        for i in range(len(self.repeat)):
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져옵니다.
            self.Bright_LED(radio_button)
    
    def blink_led_TWO(self, isParking_2):
        if 'LEFT_1' in isParking_2 and 'LEFT_2' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [9, 10, 13, 14]]
    
        elif 'LEFT_1' in isParking_2 and 'RIGHT_1' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [9, 10, 11, 12]]
    
        elif 'LEFT_1' in isParking_2 and 'RIGHT_2' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [9, 10, 15, 16]]

        elif 'LEFT_2' in isParking_2 and 'RIGHT_1' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [11, 12, 13, 14]]

        elif 'LEFT_2' in isParking_2 and 'RIGHT_2' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [5, 6, 7, 8, 13, 14, 15, 16]]

        elif 'RIGHT_1' in isParking_2 and 'RIGHT_2' in isParking_2:
            self.repeat = [x for x in self.repeat if x not in [11, 12, 15, 16]]
    
        else:
            print("에러 발생")
    
        for i in range(len(self.repeat)):
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져옵니다.
            self.Bright_LED(radio_button)

    def blink_led_ONE(self, isParking_3):
        if 'LEFT_1' not in isParking_3:
            self.repeat = [x for x in self.repeat if x in [1,2,3,4,9,10]]
    
        elif 'LEFT_2' not in isParking_3:
            self.repeat = [x for x in self.repeat if x in [1,2,3,4,5,6,7,8,13,14]]
    
        elif 'RIGHT_1' not in isParking_3:
            self.repeat = [x for x in self.repeat if x in [1,2,3,4,11,12]]

        else:   # RIGHT_2
            self.repeat = [x for x in self.repeat if x in [1,2,3,4,5,6,7,8,15,16]]
    
        for i in range(len(self.repeat)):
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져옵니다.
            self.Bright_LED(radio_button)

    def Bright_LED(self, radio_button):
        radio_button.setStyleSheet("""
            QRadioButton::indicator { 
                width: 12px; 
                height: 12px; 
                border-radius: 6px;
                background-color: yellow;
                border: 2px solid black;
            }
        """)
        
        QTimer.singleShot(250, lambda rb=radio_button: rb.setStyleSheet("""
            QRadioButton::indicator { 
                width: 12px; 
                height: 12px; 
                border-radius: 6px;
                background-color: white;
                border: 2px solid black;
            }
        """))
    
############################################################################### 

## 정보 조회 초기화
    def Clear(self):
        self.Name.setText("")
        self.Phone.setText("")
        self.carNum.setText("")
        self.Location.setText("")
        self.parkTime.setText("")
        self.entryLog.setDateTime(QDateTime(2024, 1, 1, 0, 0))
        self.Fee.hide()
        self.feeLabel.hide()
        self.parkTime.hide()
        self.parkTimeLabel.hide()

        
## 주차장 자리 최신화 ##
    # 데이터베이스 갱신을 위한 함수
    def connectDatabase(self):
        self.remote = mysql.connector.connect(
            host = "msdb.cvyy46quatrs.ap-northeast-2.rds.amazonaws.com",
            port = 3306,
            user = "root",
            password = "Dbsalstjq128!",
            database = "iot"
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
        self.parklist = {'LEFT_1': False, 'LEFT_2':False, 'RIGHT_1':False, 'RIGHT_2':False}
        
        count = 0

        for each in result:
            each = each[0]
            self.parklist[f'{each}']=True
            count += 1
        
        self.CountBox.setText(str(count))
        self.currentPlace()

    def currentPlace(self):

        if self.parklist['LEFT_1'] == True:
            self.left_1.setStyleSheet("background-color: #3498db; color: black;")
            self.left_1.setEnabled(True)
        else:
            self.left_1.setStyleSheet("background-color: #939a98; color: black;")
            self.left_1.setEnabled(False)
        
        if self.parklist['LEFT_2'] == True:
            self.left_2.setStyleSheet("background-color: #3498db; color: black;")
            self.left_2.setEnabled(True)
        else:
            self.left_2.setStyleSheet("background-color: #939a98; color: black;")
            self.left_2.setEnabled(False)
        
        if self.parklist['RIGHT_1'] == True:
            self.right_1.setStyleSheet("background-color: #3498db; color: black;")
            self.right_1.setEnabled(True)
        else:
            self.right_1.setStyleSheet("background-color: #939a98; color: black;")
            self.right_1.setEnabled(False)
        
        if self.parklist['RIGHT_2'] == True:
            self.right_2.setStyleSheet("background-color: #3498db; color: black;")
            self.right_2.setEnabled(True)
        else:
            self.right_2.setStyleSheet("background-color: #939a98; color: black;")
            self.right_2.setEnabled(False)
        
        self.else_1.setStyleSheet("background-color: #3498db; color: black;")
        self.else_1.setEnabled(False)
        self.else_2.setStyleSheet("background-color: #3498db; color: black;")
        self.else_2.setEnabled(False)
        self.else_3.setStyleSheet("background-color: #3498db; color: black;")
        self.else_3.setEnabled(False)
        self.else_4.setStyleSheet("background-color: #3498db; color: black;")
        self.else_4.setEnabled(False)
##

## 주차 정보 조회 및 주차 요금 최신화 ##
    def startDisplayCharge(self):
        self.renewtimer.running = True
        self.renewtimer.start()

    def stopDisplayCharge(self):
        self.renewtimer.running = False
        self.renewtimer.stop()


    def getInfo(self, parkPlace):
        self.stopDisplayCharge()
        self.Fee.setText("")
        self.Fee.show()
        self.feeLabel.show()
        self.parkTime.show()
        self.parkTimeLabel.show()
        self.entryLabel.show()
        self.entryLog.show()
        parkPlace = parkPlace.replace("'", '')
        sql = "select name, phone, car_num, location, entry_log from parklog where location = '" + parkPlace +"' and exit_log is NULL"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        self.showInfo(result)

    def showInfo(self, info):
        self.startDisplayCharge()
        self.Name.setText(info[0][0])
        self.Phone.setText(info[0][1])
        self.carNum.setText(info[0][2])
        self.Location.setText(info[0][3])
        dt_entry = info[0][4] + timedelta(hours=9)
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
        dt_entry = dt_entry + timedelta(hours=9)
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

        dt_time = (dt_now-dt_entry).seconds//60 #시분초를 분으로 변환

        dt_fee = (dt_day + dt_time) * fee
        
        self.Fee.setText(str(dt_fee)+"원")
        self.parkTime.setText(str(dt_time)+"분")
##

    def add_parking_image(self):
        parking_graphics_view = self.findChild(QGraphicsView, "graphicsView")

        scene = parking_graphics_view.scene()
        if scene is None:
            # 새로운 QGraphicsScene을 생성하고 graphicsView에 할당
            scene = QGraphicsScene()
            parking_graphics_view.setScene(scene)

        pixmap = QPixmap("parkinglot2.png")
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)

        view_width = 655
        view_height = 405

        # 이미지 크기를 QGraphicsView 크기에 맞게 조정
        pixmap_item.setPixmap(pixmap.scaled(view_width, view_height, Qt.IgnoreAspectRatio))

        # 이미지의 위치를 조정하려면 setPos를 사용합니다.
        pixmap_item.setPos(20, 30)  # 좌표 (0, 0)에 이미지를 배치


## 프로그램 종료 ##
    def Exit(self):
        if self.remote.is_connected():
            self.stopCurrentPlace()
            self.stopDisplayCharge()
            self.remote.close()
            print("데이터베이스 연결종료")
            exit_signal.exit_application(self.main_window)

##

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())