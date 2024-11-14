from PyQt5.QtWidgets import QApplication
import sys

def exit_application(window):
    print("프로그램 종료")
    window.close()
    QApplication.instance().quit()
    sys.exit()