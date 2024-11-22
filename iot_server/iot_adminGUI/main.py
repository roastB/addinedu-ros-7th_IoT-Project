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
import pandas as pd

Ui_MainWindow, QtBaseClass = uic.loadUiType("main.ui")

# 요금 업데이트용 스레드
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
        self.setSizeGripEnabled(True)  # 크기 조정 가능하도록 설정

        # 주차장 이미지 추가
        self.add_parking_image() 

        self.Fee.setText("")

        self.entryLog.setButtonSymbols(QDateTimeEdit.NoButtons)
        
        # 주차 자리 실시간 반영 스레드
        self.parkcount = Display()
        self.parkcount.daemon = True
        self.parkcount.update.connect(self.activateCurrentPlace)

        # 요금 정산 스레드
        self.renewtimer = Display()
        self.renewtimer.daemon = True
        self.renewtimer.update.connect(self.calculateCharge)

        # LED 제어 스레드
        self.led_update_thread = Display()
        self.led_update_thread.daemon = True
        self.led_update_thread.update.connect(self.updateLEDStatus)

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
            host = "-----",
            port = 3306,
            user = "k",
            password = "----",
            database = "----"
    )
        self.cur = self.remote.cursor()

        # 데이터베이스 커넥션 생성 시 자동 커미팅을 설정합니다.
        self.startCurrentPlace()
        self.startLEDUpdate()

        self.SalesGraph = self.findChild(QWidget, "graphicsView_2")
        if self.SalesGraph is not None:
            black_layout = QVBoxLayout(self.SalesGraph)
            self.SalesGraph.setLayout(black_layout)
            # 데이터베이스에서 데이터 가져오기
            self.load_and_plot_data(black_layout)
        else:
            print("SalesGraph:graphicsView_2 위젯을 찾을 수 없습니다.")
    
    def load_and_plot_data(self, black_layout):
        query = "SELECT exit_log, charge, location FROM parklog"
        self.cur.execute(query)
        data = self.cur.fetchall()
        
        df = pd.DataFrame(data, columns=["exit_log", "charge", "location"])
        df["exit_log"] = pd.to_datetime(df["exit_log"])+timedelta(hours=9)
        
        df["10min_interval"] = df["exit_log"].dt.floor("10min")
        charge_grouped = df.groupby("10min_interval")["charge"].sum().reset_index()
        
        x1 = charge_grouped["10min_interval"].dt.strftime('%H:%M').tolist()
        y1 = charge_grouped["charge"].tolist()
        
        location_count = df["location"].value_counts().sort_index()
        
        x2 = location_count.index.tolist()
        y2 = location_count.values.tolist()
        
        self.Graph_1 = pg.PlotWidget(self)
        black_layout.addWidget(self.Graph_1)
        self.Graph_2 = pg.PlotWidget(self)
        black_layout.addWidget(self.Graph_2)
        
        bar1 = pg.BarGraphItem(x=list(range(len(x1))), height=y1, width=0.6, brush='r')
        self.Graph_1.addItem(bar1)
        self.Graph_1.getAxis('bottom').setTicks([[(i, x1[i]) for i in range(len(x1))]])
        self.Graph_1.setTitle("10분 단위 금액")
        self.Graph_1.showGrid(x=True, y=True)
        
        bar2 = pg.BarGraphItem(x=list(range(len(x2))), height=y2, width=0.6, brush='b')
        self.Graph_2.addItem(bar2)
        self.Graph_2.getAxis('bottom').setTicks([[(i, x2[i]) for i in range(len(x2))]])
        self.Graph_2.setTitle("자리별 누적 주차 대수")
        self.Graph_2.showGrid(x=True, y=True)
        for i, value in enumerate(y1):
            text_item = pg.TextItem(text=f"{int(value)}", anchor=(0.5, -0.5), color='white')
            text_item.setPos(i, value)
            self.Graph_1.addItem(text_item)
        for i, value in enumerate(y2):
            text_item = pg.TextItem(text=f"{int(value)}", anchor=(0.5, -0.5), color='white')
            text_item.setPos(i, value)
            self.Graph_2.addItem(text_item)
        
        self.timer = QTimer(self)
        self.repeat = [ i for i in range(1, 17)]

        self.updateLEDStatus()
        self.timer.start(1000)

### 함수 ###
   
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
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져올립니다.
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
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져올립니다.
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
            radio_button = getattr(self, f"radioButton_{self.repeat[i]}")  # self.repeat의 값을 사용하여 radio button을 가져올립니다.
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
    
    def updateLEDStatus(self):
        # 주차중인 개수 및 자리 업데이트
        self.remote.close()
        self.connectDatabase()

        stillParking_sql = "SELECT p.user_id, m.name, p.location, p.exit_log FROM membership m, parklog p WHERE m.user_id = p.user_id AND p.location not LIKE 'NY' AND p.exit_log is NULL;"
        self.cur.execute(stillParking_sql)
        stillP_result = self.cur.fetchall()
        stillP_len = len(stillP_result)

        self.repeat = [i for i in range(1, 17)]

        if stillP_len == 0:  # 모든 자리 비어있음
            self.blink_led_ALL()
        elif stillP_len == 1:  # 1곳이 주차 중 (3곳이 가능)
            isParking_1 = stillP_result[0][2]
            self.blink_led_THREE(isParking_1)
        elif stillP_len == 2:  # 2곳이 주차 중 (2곳이 가능)
            isParking_2 = [stillP_result[i][2] for i in range(2)]
            self.blink_led_TWO(isParking_2)
        elif stillP_len == 3:  # 3곳이 주차 중 (1곳이 가능)
            isParking_3 = [stillP_result[i][2] for i in range(3)]
            self.blink_led_ONE(isParking_3)
        else:
            print("죄송합니다. 현재는 만차입니다. 주차할 곳이 없습니다.")


## 정보 조회 초기화 ##
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
    # 데이터베이스 경시를 위한 함수
    def connectDatabase(self):
        self.remote = mysql.connector.connect(
            host = "-----",
            port = 3306,
            user = "k",
            password = "----",
            database = "----"
    )
        self.cur = self.remote.cursor()

    def startCurrentPlace(self):
        self.parkcount.running = True
        self.parkcount.start()

    def stopCurrentPlace(self):
        self.parkcount.running = False
        self.parkcount.stop()

    def startLEDUpdate(self):
        self.led_update_thread.running = True
        self.led_update_thread.start()

    def stopLEDUpdate(self):
        self.led_update_thread.running = False
        self.led_update_thread.stop()

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
        sql = "select m.name, m.phone, c.car_num, p.location, p.entry_log from membership m join parklog p on p.user_id = m.user_id join car c on m.user_id = c.user_id where p.location = '" + parkPlace +"' and p.exit_log is NULL"
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
        sql = "select p.entry_log, c.kind_name from parklog p join c.kind_name on p.user_id = c.user_id join membership m on p.user_id = m.user_id where m.name like '%"+self.Name.text()+"' and p.exit_log is NULL"
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
            dt_day = (dt_now-dt_entry).days*1440  #일을 분으로 변화
        except:
            pass

        dt_time = (dt_now-dt_entry).seconds//60 #시분초를 분으로 변화

        dt_fee = (dt_day + dt_time) * fee
        
        self.Fee.setText(str(dt_fee)+"원")
        self.parkTime.setText(str(dt_time)+"분")

    def add_parking_image(self):
        parking_graphics_view = self.findChild(QGraphicsView, "graphicsView")

        scene = parking_graphics_view.scene()
        if scene is None:
            # 새로운 QGraphicsScene을 생성하고 graphicsView에 할당
            scene = QGraphicsScene()
            parking_graphics_view.setScene(scene)

        pixmap = QPixmap("image/parkinglot2.png")
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)

        view_width = 655
        view_height = 405

        pixmap_item.setPixmap(pixmap.scaled(view_width, view_height, Qt.IgnoreAspectRatio))

        pixmap_item.setPos(20, 30)  # 자포 (0, 0)에 이미지를 배치


## 프로그램 종료 ##
    def Exit(self):
        if self.remote.is_connected():
            self.stopCurrentPlace()
            self.stopDisplayCharge()
            self.stopLEDUpdate()
            self.remote.close()
            print("데이터베이스 연결종료")
            exit_signal.exit_application(self.main_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())

