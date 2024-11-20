import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import QDateTime
import mysql.connector
import exit_signal

from_class = uic.loadUiType("record.ui")[0]

class WindowClass(QMainWindow, from_class):
    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.main_window = main_window
        self.detailGroupBox.hide()

        # mysql 접속
        self.remote = mysql.connector.connect(
            host = "****",
            port = 3306,
            user = "****",
            password = "****!",
            database = "****"
        )
        self.cursor = self.remote.cursor()

        # [1] ID, 이름, 전화번호, 차량번호, 차종, 주차위치, RFID
        self.cursor.execute("SELECT DISTINCT id FROM membership")
        dbid = self.cursor.fetchall()

        self.cursor.execute("SELECT DISTINCT name FROM membership")
        dbname = self.cursor.fetchall()
        name_list = ["ALL"] + [row[0] for row in dbname]

        self.cursor.execute("SELECT DISTINCT phone FROM membership")
        dbphone = self.cursor.fetchall()
        phone_list = ["ALL"] + [row[0] for row in dbphone]
        
        self.cursor.execute("SELECT DISTINCT car_num FROM membership")
        dbcarnum = self.cursor.fetchall()
        car_num_list = ["ALL"] + [row[0] for row in dbcarnum]

        self.cursor.execute("SELECT DISTINCT kind FROM membership")
        dbkind = self.cursor.fetchall()
        car_kind_list = ["ALL"] + [row[0] for row in dbkind]

        self.cursor.execute("SELECT DISTINCT location FROM parklog")
        dblocation = self.cursor.fetchall()
        location_list = ["ALL"] + [row[0] for row in dblocation]

        self.cursor.execute("SELECT DISTINCT RFID FROM membership")
        dbrfid = self.cursor.fetchall()
        rfid_list = ["ALL"] + [row[0] for row in dbrfid]

        # [2] QComboBox : DB에서 가져온 목록을 바탕으로!
        for idx in range(len(dbid)+1):
            self.nameBox.addItem(str(name_list[idx]))
            self.phoneBox.addItem(str(phone_list[idx]))
            self.carNumBox.addItem(str(car_num_list[idx]))
            self.rfidBox.addItem(str(rfid_list[idx]))
        
        for idx in range(len(location_list)):
            self.locationBox.addItem(str(location_list[idx]))

        for idx in range(len(car_kind_list)):
            self.carKindBox.addItem(str(car_kind_list[idx]))

        self.init_carInDT_1 = self.carInDT_1.dateTime()
        self.init_carInDT_2 = self.carInDT_2.dateTime()
        self.init_carOutDT_1 = self.carOutDT_1.dateTime()
        self.init_carOutDT_2 = self.carOutDT_2.dateTime()

        self.ResizeWidget()

        # [핵심 코드]
        self.btnSearch.clicked.connect(self.Search)
        self.btnMore.clicked.connect(self.MoreInfo)
        self.btnReset.clicked.connect(self.Reset)
        self.btnDBClear.clicked.connect(self.RecordClear)
        self.btnExit.clicked.connect(self.Exit)

    def ResizeWidget(self):
        # RecordWidget size 조정
        auto_size = [1, 4, 5, 6]
        for i in auto_size:
            self.dbRecordWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)
        self.dbRecordWidget.setColumnWidth(0, 50) #RFID
        self.dbRecordWidget.setColumnWidth(2, 110) #RFID
        self.dbRecordWidget.setColumnWidth(3, 100) #전화번호
        self.dbRecordWidget.setColumnWidth(7, 155) #입차시간
        self.dbRecordWidget.setColumnWidth(8, 155) #출차시간


    def Search(self):
        self.ResizeWidget()
        name = self.nameBox.currentText()
        phone_num = self.phoneBox.currentText()
        car_num = self.carNumBox.currentText()
        location = self.locationBox.currentText()
        car_kind = self.carKindBox.currentText()
        rfid = self.rfidBox.currentText()

        carInDT_1 = self.carInDT_1.dateTime().toString("yyyyMMddhhmmss")
        carInDT_2 = self.carInDT_2.dateTime().toString("yyyyMMddhhmmss")
        carOutDT_1 = self.carOutDT_1.dateTime().toString("yyyyMMddhhmmss")
        carOutDT_2 = self.carOutDT_2.dateTime().toString("yyyyMMddhhmmss")

        params = [carInDT_1, carInDT_2, carOutDT_1, carOutDT_2]
        query = """
                SELECT 
                    m.id, m.name, m.RFID, m.phone, m.car_num, m.kind, 
                    p.location, p.entry_log, p.exit_log 
                FROM 
                    membership m, parklog p
                WHERE 
                    m.name = p.name AND m.car_num = p.car_num
                AND
                    entry_log between %s AND %s
                AND
                    exit_log between %s AND %s
                ORDER BY p.entry_log DESC
                """
        
        if (name != "ALL"):
            query += "AND m.name = %s"
            params.append(name)

        if (phone_num != "ALL"):
            query += "AND m.phone = %s"
            params.append(phone_num)

        if (car_num != "ALL"):
            query += "AND m.car_num = %s"
            params.append(car_num)

        if (location != "ALL"):
            query += "AND p.location = %s"
            params.append(location)

        if (car_kind != "ALL"):
            query += "AND m.kind = %s"
            params.append(car_kind)
        
        if (rfid != "ALL"):
            query += "AND m.RFID = %s"
            params.append(rfid)

        # 최종 Qurey문 실행
        self.cursor.execute(query, params)
        results = self.cursor.fetchall()

        self.dbRecordWidget.setRowCount(len(results))
        for row_idx, row_data in enumerate(results):
            for col_idx, col_data in enumerate(row_data):
                self.dbRecordWidget.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))


    def MoreInfo(self):
        if self.detailGroupBox.isVisible():
            self.detailGroupBox.hide()
        else:
            self.detailGroupBox.show()


    def Reset(self):
        self.nameBox.setCurrentText("ALL")
        self.phoneBox.setCurrentText("ALL")
        self.carNumBox.setCurrentText("ALL")
        self.rfidBox.setCurrentText("ALL")
        self.locationBox.setCurrentText("ALL")
        self.carKindBox.setCurrentText("ALL")

        self.carInDT_1.setDateTime(self.init_carInDT_1)
        self.carInDT_2.setDateTime(self.init_carInDT_2)
        self.carOutDT_1.setDateTime(self.init_carOutDT_1)
        self.carOutDT_2.setDateTime(self.init_carOutDT_2)

        self.dbRecordWidget.setRowCount(0)
        print("속성값 모두 Reset")

    def RecordClear(self):
        retval = QMessageBox.warning(self, "parklog DB Reset",
                                      """⛔ "parklog DB"를 초기화 하실건가요?""",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if retval == QMessageBox.Yes:
            delete_query = "DELETE FROM parklog"
            self.cursor.execute(delete_query)   # delete_query 실행
            self.remote.commit()                # 변경 사항을 커밋하여 DB에 저장
            QMessageBox.about(self, "parklog DB Reset", "🟢 parklog DB : 초기화 되었습니다.")
            print("parklog DB : 초기화 되었습니다.")

        else:
            print("parklog DB : 초기화 취소")


    def Exit(self):
        if self.remote.is_connected():
            self.remote.close()
            print("데이터베이스 연결종료")
            exit_signal.exit_application(self.main_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())
