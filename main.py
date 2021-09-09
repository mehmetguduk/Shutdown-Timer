import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMenu, QAction, QSystemTrayIcon, QMessageBox, qApp
from interface import Ui_MainWindow
from datetime import datetime
from PyQt5.QtCore import QDate, QTime, QTimer, Qt
from PyQt5.QtGui import QIcon


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

Logo = resource_path("logo.ico")

    
class myApp(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        """__Connections__"""
        self.ui.btn_start_DATETIME.clicked.connect(self.button_DATETIME)
        self.ui.btn_start_STOPWATCH.clicked.connect(self.button_STOPWATCH)
        self.ui.btn_cancel.clicked.connect(self.cancel)
        self.ui.lbl_copyright.setOpenExternalLinks(True)

        """__Tray action settings__"""
        self.tray_icon = QSystemTrayIcon(self)
        self.icon = QIcon(Logo)
        self.tray_icon.setIcon(self.icon)
        show_action = QAction("Show", self)
        quit_action = QAction("Exit", self)
        hide_action = QAction("Hide", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        """__Timer settings__"""
        self.count = 0
        self.start = False
        timer = QTimer(self)
        timer.timeout.connect(self.timer)
        timer.start(100)
        self.ui.lbl_TIMER.setVisible(0)
        
        """__Setting comboBox item align to center__"""
        self.ui.comboBox.setEditable(True)
        line_edit = self.ui.comboBox.lineEdit()
        line_edit.setAlignment(Qt.AlignCenter)
        line_edit.setReadOnly(True)

        """__Inserting current date and time__"""
        current_date = str(datetime.now()).split(" ")[0].split("-")
        date = QDate(int(current_date[0]), int(current_date[1]), int(current_date[2]))
        self.ui.dateTimeEdit_DATE.setDate(date)
        current_time = str(datetime.now()).split(" ")[1].split(":")
        time = QTime(int(current_time[0]), int(current_time[1]))
        self.ui.timeEdit_DATE.setTime(time)

    def button_DATETIME(self):
        date = self.ui.dateTimeEdit_DATE.text()
        time = self.ui.timeEdit_DATE.text()

        input_date_and_time = datetime.strptime(f"{date} {time}", '%d/%m/%Y %H:%M')
        current_date_and_time = datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M')
        current_date_and_time = datetime.strptime(current_date_and_time, '%d/%m/%Y %H:%M')
        difference = int((input_date_and_time - current_date_and_time).total_seconds())
        
        if difference == 0:
            label = f"Are you sure do you want to {self.ui.comboBox.currentText()} now?"
            question = QMessageBox.question(self, "Confirmation", label,  QMessageBox.Yes | QMessageBox.No)
            if question == QMessageBox.Yes:
                difference = 1
            self.getting_second(difference)
        elif difference < 0:
            label = f"{date} {time} is a old time."
            QMessageBox.information(self, "Error", label, QMessageBox.Ok)
        else:
            label = f"{self.ui.comboBox.currentText()} has been set on {date} {time}."
            QMessageBox.information(self, "Successed", label, QMessageBox.Ok)
            self.getting_second(difference)

    def button_STOPWATCH(self):
        hour = self.ui.spinBox_HOUR.text()
        minute = self.ui.spinBox_MINUTE.text()
        second = self.ui.spinBox_SECOND.text()

        hour = int(hour)*3600
        minute = int(minute)*60
        second = int(second)
        total_second = hour + minute + second

        hours = divmod(total_second,3600)[0]
        minutes = divmod(total_second-(hours*3600),60)[0]
        remaining_seconds = total_second-((hours*3600)+(minutes*60))
        if remaining_seconds == 0 and hours == 0 and minutes == 0:
            time_label = ""
            label = f"Are you sure do you want to {self.ui.comboBox.currentText()} now?"
            question = QMessageBox.question(self, "Confirmation", label,  QMessageBox.Yes | QMessageBox.No)
            if question == QMessageBox.Yes:
                total_second = 1
            self.getting_second(total_second)
        elif hours > 0:
            time_label = f"{hours} hr {minutes} min {remaining_seconds} sec"
        elif hours == 0 and minutes > 0:
            time_label = f"{minutes} min {remaining_seconds} sec"
        elif hours == 0 and minutes == 0:
            time_label = f"{remaining_seconds} sec"
            
        if time_label != "":
            label = f"{self.ui.comboBox.currentText()} will be happen in {time_label}."
            QMessageBox.information(self, "Successed", label, QMessageBox.Ok)

        self.getting_second(total_second)

    def getting_second(self, second):
        global starting_point_for_progress_bar
        starting_point_for_progress_bar = int(second)
        self.count = second * 10
        self.ui.lbl_TIMER.setText(str(second))
        self.start = True
        if self.count == 0:
            self.start = False
        
    def timer(self):
        if self.start:
            self.count -= 1
            value = 100 - ((100 * int(float(self.ui.lbl_TIMER.text()))) / starting_point_for_progress_bar)
            self.ui.progressBar.setValue(int(value))
            if self.count == 0:
                self.start = False
                self.ui.lbl_TIMER.setText("0")
                self.action()
        if self.start:
            text = str(self.count / 10)
            self.ui.lbl_TIMER.setText(text)
  
    def action(self):
        combobox_item = self.ui.comboBox.currentText()
        if combobox_item == "Shutdown":
            os.system("shutdown /f /s /t 0")
        elif combobox_item == "Restart":
            os.system("shutdown /f /r /t 0")
        elif combobox_item == "Log off":
            os.system("shutdown /f /l")
        elif combobox_item == "Hibernate":
            os.system("%windir%/System32/rundll32.exe powrprof.dll,SetSuspendState Hibernat")

    def cancel(self):
        self.start = False
        self.count = 0
        self.ui.lbl_TIMER.setText("0")
        self.ui.progressBar.setValue(0)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("Shutdown Timer","Application has minimized to Tray",QSystemTrayIcon.Information)



if __name__ == '__main__': 
    app = QtWidgets.QApplication(sys.argv)
    win = myApp()
    win.show()
    sys.exit(app.exec_())