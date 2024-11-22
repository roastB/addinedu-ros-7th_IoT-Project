import sys
from PyQt5.QtWidgets import *
from park_user_1 import WindowClass as pu1
from main import WindowClass as m
from record import WindowClass as r

# dev tag name : v1.0 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parking Management")
        self.resize(950, 950)
        tabs = QTabWidget()


        tabs = QTabWidget()
        self.pu1_tab = pu1(self)  # Sign Up 탭
        self.m_tab = m(self)      # Monitoring 탭
        self.r_tab = r(self)      # Parking Log 탭

        tabs.addTab(self.pu1_tab, "Sign Up")
        tabs.addTab(self.m_tab, "Monitoring")
        tabs.addTab(self.r_tab, "Parking Log")

        self.setCentralWidget(tabs)

        tabs.currentChanged.connect(self.update_tab)

        tabs.setStyleSheet("""
        QTabWidget::pane {
            border-top: 2px solid #C2C7CB;
            position: absolute;
            top: -0.5em;
        }
        QTabBar::tab {
            background: #f0f0f0;
            padding: 10px 20px;
            border: 1px solid #C2C7CB;
            border-bottom: none;
            border-radius: 5px 5px 0 0;
            font-size: 12px;
            font-weight: bold;
            min-width: 100px;
        }
        QTabBar::tab:selected {
            background: #FFFFFF;
            color: #00daa9
        }
        QTabBar::tab:!selected {
            background: #C2C7CB;
            margin-top: 2px;
            color: #555555;
        }
        """)

    def update_tab(self, index):
        # 탭에 맞는 업데이트 메서드 호출
        if index == 0:  # Sign Up 탭
            self.pu1_tab.update()
        elif index == 1:  # Monitoring 탭
            self.m_tab.update()
        elif index == 2:  # Parking Log 탭
            self.r_tab.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = MainWindow()
    myWindows.show()


    sys.exit(app.exec_())