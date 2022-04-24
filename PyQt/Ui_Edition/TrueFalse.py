import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
from Meters import get_coordinate, clock_max, clock_min, clear_list
import sqlite3


class TrueFalseWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/TrueFalseWindow.ui', self)
        self.initUI()

    def initUI(self):
        self.ComleteBut.clicked.connect(self.main_func)
        self.BackButton.clicked.connect(self.back)

    def back(self):  # кнопка для закрытия окна
        self.close()

    def main_func(self):
        self.label_3.setText('')  # каждый раз при нажатии на кнопку текст ошибки очищается
        self.ResultText.setText('')  # и текст результата
        try:
            #  полученние данных из соответсвующих виджетов
            tr1 = int(self.Train1.text())
            tr2 = int(self.Train2.text())
            f = open('data/db_info.txt')
            reading = f.read()  # узнаём путь к БД из файла
            f.close()
            working_object = sqlite3.connect(reading)
            cur = working_object.cursor()  # создаём курсор, для работы БД
            # узнаем напраление составов
            tr1_direct, = cur.execute("""SELECT direction FROM main 
                                    WHERE number = ?""", (tr1,)).fetchone()
            tr2_direct, = cur.execute("""SELECT direction FROM main 
                                    WHERE number = ?""", (tr2,)).fetchone()
            # будем считать, что на нашей дороге два пути: туда и обратно
            if tr1_direct != tr2_direct:  # когда они едут в разную сторону они никак не встретяться
                self.ResultText.setText('Не встретятся')
            else:
                tr1_time_list = cur.execute("""SELECT time  FROM main 
                                        WHERE number = ?""", (tr1,)).fetchall()
                clear_list(tr1_time_list)
                tr2_time_list = cur.execute("""SELECT time FROM main 
                                        WHERE number = ?""", (tr2,)).fetchall()
                clear_list(tr2_time_list)
                # стартовым временем будем считать, тот момент, когда каждый поез находится в движен
                start_time = clock_max([clock_min(tr1_time_list), clock_min(tr2_time_list)])
                # будем считать, что они не могут одновременно находиться на одной станции
                if get_coordinate(tr1, start_time) == get_coordinate(tr2, start_time):
                    self.ResultText.setText('ВСТРЕТЯТСЯ!!!')
                # далее определяется, кто из них ближе к нулю
                if get_coordinate(tr1, start_time) < get_coordinate(tr2, start_time):
                    first_tr, second_tr = tr1, tr2
                else:
                    first_tr, second_tr = tr2, tr1

                finish_time = clock_min([clock_max(tr1_time_list), clock_max(tr2_time_list)])
                if get_coordinate(second_tr, finish_time) <= get_coordinate(first_tr, finish_time):
                    self.ResultText.setText('ВСТРЕТЯТСЯ!!!')
                    # т.к. превый обогнал второго, а значит был момент выстречи
                else:
                    self.ResultText.setText('Не встретятся')
        except:
            self.label_3.setText('Введены некоректные данные!')
            # в случае, если пользователь ввёл не существующий номер поезда


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = TrueFalseWindow()
    prog.show()
    sys.exit(app.exec_())
