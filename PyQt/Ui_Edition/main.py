import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from Settings import SettingsWindow
from Meters import MetersWindow
from TrueFalse import TrueFalseWindow
from Timetable import TimetableWindow
from TimetableEdit import TimetableEditWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/MainWindow.ui', self)
        self.initUI()

    def initUI(self):
        self.SettingsButton.setText('\u2699')
        icon = QPixmap('data/train.jpg')
        self.RGD.setPixmap(icon)
        self.SettingsButton.clicked.connect(self.setting_but)
        self.RunButton.clicked.connect(self.run)

    def setting_but(self):  # открытие настроек
        self.settings = SettingsWindow()
        self.settings.show()

    def run(self):  # открывается окно, соответсвующие выбранному в комбо боксе
        choice = self.comboBox.currentText()
        if choice == 'Расстояние':
            self.open_window = MetersWindow()
            self.open_window.show()
        elif choice == 'Проверка на встречу':
            self.open_window = TrueFalseWindow()
            self.open_window.show()
        elif choice == 'Расписание':
            self.open_window = TimetableWindow()
            self.open_window.show()
        elif choice == 'Изменение расписания':
            self.open_window = TimetableEditWindow()
            self.open_window.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = MainWindow()
    prog.show()
    sys.exit(app.exec_())
