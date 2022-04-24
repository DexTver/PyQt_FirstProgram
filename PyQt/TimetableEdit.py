import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
import sqlite3
from designs.TimetableEditWindow import Ui_TimetableEditWindow


class TimetableEditWindow(QWidget, Ui_TimetableEditWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.n = 0

    def initUI(self):
        self.BackButton.clicked.connect(self.back)
        self.completeButton.clicked.connect(self.main_func)
        self.switchBut.clicked.connect(self.switch_func)

    def back(self):  # кнопка для закрытия окна
        self.close()

    def switch_func(self):  # замена интерфейса для другого режима
        if self.n == 0:
            self.numberTextEdit.resize(0, 0)
            self.label.setText('Станция:')
            self.switchLabel.setText('Режим: изменение станций')
            self.label_2.setText('')
            self.label_4.setText('')
            self.label_3.setText('Координаты:')
            self.directionTextEdit.resize(0, 0)
            self.timeTextEdit.resize(101, 41)
            self.stationTextEdit.move(20, 110)
            self.stationTextEdit.resize(281, 41)
            self.timeTextEdit.setPlainText('')
            self.n = 1
        else:
            self.stationTextEdit.move(110, 110)
            self.stationTextEdit.resize(191, 41)
            self.numberTextEdit.resize(91, 41)
            self.directionTextEdit.resize(31, 41)
            self.timeTextEdit.resize(71, 41)
            self.timeTextEdit.setPlainText('')
            self.label_3.setText('Время:')
            self.label.setText('Номер поезда:')
            self.label_2.setText('Станция:')
            self.label_4.setText('=>')
            self.switchLabel.setText('Режим: добавить прибытие поезда')
            self.n = 0

    def main_func(self):
        self.resLabel.setText('')  # очистка лэйбла
        f = open('data/db_info.txt')
        reading = f.read()
        f.close()
        working_object = sqlite3.connect(reading)
        cur = working_object.cursor()
        # возьмём информацию из текстовых полей
        tr_number = self.numberTextEdit.toPlainText()
        tr_station = self.stationTextEdit.toPlainText()
        tr_time = self.timeTextEdit.toPlainText()
        tr_direction = self.directionTextEdit.toPlainText()
        try:
            if tr_number and tr_direction:
                tr_number, tr_direction = int(tr_number), int(tr_direction)
            if self.n == 1:
                tr_time = int(tr_time)
            choice = self.comboBox.currentText()  # узнаем, какая функция выбрана и пользователя
            if choice == 'Удалить':
                if tr_number:
                    object = cur.execute("""SELECT * FROM main 
                                        WHERE number = ? and station = ? 
                                        and time = ? and direction = ?""",
                                         (tr_number, tr_station, tr_time, tr_direction)).fetchall()
            # возьмём объект с соответсвующими параметрами, если он существует, то выполним действия
                    if object:
                        cur.execute("""DELETE from main 
                                    WHERE number = ? and station = ? 
                                    and time = ? and direction = ?""",
                                    (tr_number, tr_station, tr_time, tr_direction))
                        valid = QMessageBox.question(  # откроем окно подтверждения
                            self, '', "Действительно удалить элементы?",
                            QMessageBox.Yes, QMessageBox.No)
                        if valid:  # подтвердим изменения в БД
                            working_object.commit()
                            self.resLabel.setText('Успешно!')
                    else:  # если не существует, сообщим об этом пользователю
                        self.resLabel.setText('Объект отсутвует!')
                else:
                    object = cur.execute("""SELECT * FROM stations 
                                                        WHERE station = ?""",
                                         (tr_station,)).fetchall()
            # возьмём объект с соответсвующими параметрами, если он существует, то выполним действия
                    if object:
                        cur.execute("""DELETE from stations 
                                                    WHERE station = ?""",
                                    (tr_station,))
                        valid = QMessageBox.question(  # откроем окно подтверждения
                            self, '', "Действительно удалить элементы?",
                            QMessageBox.Yes, QMessageBox.No)
                        if valid:  # подтвердим изменения в БД
                            working_object.commit()
                            self.resLabel.setText('Успешно!')
                    else:  # если не существует, сообщим об этом пользователю
                        self.resLabel.setText('Объект отсутвует!')
            elif choice == 'Добавить':  # соответсвенно добавим объект в БД
                if tr_number:
                    cur.execute("""INSERT INTO main 
                                VALUES (?, ?, ?, ?)""",
                                (tr_number, tr_station, tr_time, tr_direction))
                    valid = QMessageBox.question(  # откроем окно подтверждения
                        self, '', "Действительно добавить элементы?",
                        QMessageBox.Yes, QMessageBox.No)
                    if valid:  # подтвердим изменения в БД
                        working_object.commit()
                        self.resLabel.setText('Успешно!')
                else:
                    cur.execute("""INSERT INTO stations
                                                VALUES (?, ?)""",
                                (tr_station, tr_time))
                    valid = QMessageBox.question(  # откроем окно подтверждения
                        self, '', "Действительно добавить элементы?",
                        QMessageBox.Yes, QMessageBox.No)
                    if valid:  # подтвердим изменения в БД
                        working_object.commit()
                        self.resLabel.setText('Успешно!')
        except:  # в случае, если пользователь ввёл не число в номер поезда, либо направления
            self.resLabel.setText('Неверный формат!')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = TimetableEditWindow()
    prog.show()
    sys.exit(app.exec_())
