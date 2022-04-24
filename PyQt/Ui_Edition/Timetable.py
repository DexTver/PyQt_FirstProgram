import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic
from Meters import clear_list
import sqlite3
import pymorphy2


def time_delta(a, b):  # функция для расчёта времени, за которое совершается путь
    a, b = a.split(':'), b.split(':')
    hours = int(b[0]) - int(a[0])  # вычитается из предпологаемо большего времпени меньшее
    if int(b[1]) < int(a[1]):  # если количество минут в большем вермени нужно вычесть ещё один час,
        mins = int(b[1]) - int(a[1]) + 60  # а к минутам добавить 60
        hours -= 1
    else:
        mins = int(b[1]) - int(a[1])

    morph = pymorphy2.MorphAnalyzer()  # далее получившиеся разница преобразуется в красивый вид
    if hours:  # этот иф на тот случай, если разница получилась меньше часа, тогда мы в него не
        word = morph.parse('час')[0]  # зайдём и будем выводить строку только с минутами
        word2 = morph.parse('минута')[0]
        res = f'{hours} {word.make_agree_with_number(hours).word} '
        res += f'{mins} {word2.make_agree_with_number(mins).word}'
        return res
    word2 = morph.parse('минута')[0]
    res = f'{mins} {word2.make_agree_with_number(mins).word}'
    return res


class TimetableWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('designs/TimetableWindow.ui', self)
        self.initUI()
        self.n = 1

    def initUI(self):
        self.BackButton.clicked.connect(self.back)
        self.ComleteBut.clicked.connect(self.main_func)
        self.reverseBut.clicked.connect(self.reverse)

    def back(self):  # кнопка для закрытия окна
        self.close()

    def reverse(self):  # кнопка для замены местами двух слов
        if self.n % 2 == 0 and self.n > 0:
            text = self.InputLine.text()
            text2 = self.InputLine_2.text()
            self.n += 1
            self.InputLine.setText(text2)
            self.InputLine_2.setText(text)
        else:
            text = self.InputLine_2.text()
            text2 = self.InputLine.text()
            self.n += 1
            self.InputLine.setText(text)
            self.InputLine_2.setText(text2)

    def main_func(self):
        self.label.setText('')
        res = ''  # в случае поаторного нажатия на кнопку лейбл и результат очищаются
        start_station = self.InputLine.text()
        finish_station = self.InputLine_2.text()  # берём название станции отправления и назначения
        # далее открываем БД
        f = open('data/db_info.txt')
        reading = f.read()
        f.close()
        working_object = sqlite3.connect(reading)
        cur = working_object.cursor()
        # далее находим номера поездов, которые могут побывать на станции, которая введена пользоват
        num = cur.execute("""SELECT number FROM main
                                WHERE station = ? or station = ?""",
                          (start_station, finish_station)).fetchall()
        clear_list(num)  # для удобной работы "очищаем" список
        numbers = []
        for i in range(len(num)):  # проверка на то, что поезд может побывать на всех двух станциях
            if num.count(num[i]) == 2:
                numbers.append(num[i])
        numbers = list(set(numbers))
        # по итогу остались поезда, которые могут побывать на этих станция, осталось вывести время
        for j in range(len(numbers)):  # их прибытия
            train_type, = cur.execute("""SELECT type FROM trains 
                                        WHERE number = ?""", (int(numbers[j]),)).fetchone()
            start_time, = cur.execute("""SELECT time FROM main 
                                        WHERE number = ? and station = ?""",
                                      (int(numbers[j]), start_station)).fetchone()
            finish_time, = cur.execute("""SELECT time FROM main 
                                        WHERE number = ? and station = ?""",
                                       (int(numbers[j]), finish_station)).fetchone()
            ans = time_delta(start_time, finish_time)
            if ans[0] != '-':
                # в случае, если время от станции А до Б оказалось полодительным  (поезд двигается
                res += f'{start_time} -> {finish_time}({ans}) '  # в нужном направлении), выводим
                res += f'Поезд: {train_type}\n'  # соответсвующие данные для этого поезда
        if not res:  # если пользователь ввёл не существающую станцию, либо нет составов, которые
            self.label.setText('Нет подходящих составов!')  # ему подходят - выведем сообщение
        self.ResultBrowser.setText(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = TimetableWindow()
    prog.show()
    sys.exit(app.exec_())
