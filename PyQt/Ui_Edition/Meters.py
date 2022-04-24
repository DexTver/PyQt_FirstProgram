import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
import sqlite3


def clock_max(sp):
    res = max(sp, key=lambda x: (int(x[0]), int(x[1])))
    return res
    #  эта функция находит максимальное вермя из списка


def clock_min(sp):
    res = min(sp, key=lambda x: (int(x[0]), int(x[1])))
    return res
    #  эта функция находит минимальное вермя из списка


def clear_list(sp):
    for i in range(len(sp)):
        sp[i] = str(sp[i]).strip("('') ,")
        if ':' in sp[i]:
            sp[i] = sp[i].split(':')
    # эта функция очищает список от лишних символов, преобразуя его в список удобный для работы


def clear_str(st):
    res = st.split(':')
    return res
    # аналагична clear_list


def compare(fr_t, sc_t):
    if int(fr_t[0]) == int(sc_t[0]):
        if int(fr_t[1]) > int(sc_t[1]):
            return True
        return False
    else:
        if int(fr_t[0]) > int(sc_t[0]):
            return True
        return False
    #  эта функция используется для сравнения двух времён


def cst(time):  # construction
    res = f'{time[0]}:{time[1]}'
    return res
    # эта функция используется для форматирования времени


def get_coordinate(train_number, train_time):
    if len(train_time) == 2:
        train_time = cst(train_time)
    f = open('data/db_info.txt')
    reading = f.read()
    f.close()
    working_object = sqlite3.connect(reading)
    cur = working_object.cursor()
    # откроем базу данных, чтобы с ней работать
    time_list = list(cur.execute("""SELECT time FROM main 
                        WHERE number = ?""", (train_number,)).fetchall())
    clear_list(time_list)
    #  далее происходит поиск предыдущей станции, чтобы уже от её координат начать отсчёт движения
    #  сначала ищем время, когда состав находился на станции
    s = 1
    train_time = clear_str(train_time)
    if train_time in time_list and train_time != clock_max(time_list) and train_time != clock_min(
            time_list):
        last_station_time = train_time
    elif not compare(train_time, clock_max(time_list)) and compare(train_time,
                                                                   clock_min(time_list)):
        time_list.append(train_time)
        time_list = sorted(time_list, key=lambda x: (int(x[0]), int(x[1])))
        time_index = time_list.index(train_time)
        last_station_time = time_list[time_index - 1]
    elif train_time == clock_max(time_list) or compare(train_time, clock_max(time_list)):
        last_station_time = clock_max(time_list)
        s = 0
    else:
        last_station_time = clock_min(time_list)
        s = 0
    # затем имея время, когда мы находились на предыдущей станции, найдём эту станцию
    last_station, = cur.execute("""SELECT station FROM main WHERE number = ? and time = ?""",
                                (train_number, cst(last_station_time))).fetchone()
    delta_time = (int(train_time[0]) - int(last_station_time[0])) * 3600 + (
            int(train_time[1]) - int(last_station_time[1])) * 60
    # найдём время, которое поезд был в движении
    type_of_train, = cur.execute("""SELECT type FROM trains WHERE number = ?""",
                                 (train_number,)).fetchone()
    max_speed, a = cur.execute("""SELECT max_speed, a FROM types WHERE type = ?""",
                               (type_of_train,)).fetchone()
    max_speed, a = (int(max_speed) / 3.6), float(a)
    #  берём из БД пареметры поезда
    if abs(delta_time) < (max_speed / a) and s:
        s = delta_time ** 2 * a / 2
    elif delta_time > 0 and s:
        s = (delta_time + delta_time - max_speed / a) / 2 * max_speed
    else:
        s = 0
    #  переменная s хранит расстояние, которое преодолел поезд отъехав от предыдущей станции
    direct, = cur.execute("""SELECT direction FROM main WHERE number = ? and station = ?""",
                          (train_number, last_station)).fetchone()
    coord, = cur.execute("""SELECT distance FROM stations WHERE station = ?""",
                         (last_station,)).fetchone()
    #  переменная coord содержит координаты предыдущей станции
    if direct == 0:
        coord -= s / 1000
        return coord
    coord += s / 1000
    return coord
    #  в зависимости от направления добовляем или отнимаем пройденный путь, что бы получить
    #  координаты поезда в момент времени относительно нуля


class MetersWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/MetersWindow.ui', self)
        self.initUI()

    def initUI(self):
        self.ComleteBut.clicked.connect(self.main_func)
        self.BackButton.clicked.connect(self.back)

    def back(self):  # кнопка для закрытия окна
        self.close()

    def main_func(self):
        self.error_label.setText('')
        try:
            # получим данные из окна
            time = ((str(self.timeEdit.time()).lstrip('PyQt5.QtCore.QTime')).strip('()')).split(
                ', ')
            tr1 = int(self.Train1.text())
            tr2 = int(self.Train2.text())
            #  найдём координаты каждого поезда
            r1 = get_coordinate(tr1, time)
            r2 = get_coordinate(tr2, time)
            #  найдём модуль разности двух координат и выведим красиво
            self.ResultText.setText(f'~{str(round(abs(r1 - r2), 3))}км')
        except:
            #  в случае, если пользователь ввёл номер поезда, которого не существует, то
            #  выведем ему соответсвующее сообщение
            r = 'Произошла непредвиденная ошибка!'
            r += '\nПроверьте корректность запроса (но-\nмера поездов).'
            self.error_label.setText(r)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = MetersWindow()
    prog.show()
    sys.exit(app.exec_())
