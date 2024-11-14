import sys
from PyQt5.QtWidgets import *
from park_user_1 import WindowClass as pu1
from main import WindowClass as m


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Tabs Example")
        self.resize(950, 950)
        tabs = QTabWidget()
        tabs.addTab(pu1(self), "Sign Up")
        tabs.addTab(m(self), "Administration")
        self.setCentralWidget(tabs)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = MainWindow()
    myWindows.show()


    sys.exit(app.exec_())