import sys
from PyQt5.QtWidgets import QWidget, QFileDialog, QApplication
from designs.SettingsWindow import Ui_Settings


class SettingsWindow(QWidget, Ui_Settings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        file = open('data/db_info.txt')
        #  в этом файле будет храниться путь к выбранной БД
        message = file.read()
        self.DBText.setPlainText(message)
        #  изначально в этом окне будет отображаться БД, которая храниться в файле
        file.close()
        self.BackButton.clicked.connect(self.back)
        self.CompleteBut.clicked.connect(self.db_rewriting)
        self.ChoiceBut.clicked.connect(self.choice_db)

    def back(self):  # кнопка для закрытия окна
        self.close()

    def db_rewriting(self):
        file = open('data/db_info.txt', 'w')
        res = self.DBText.toPlainText()
        #  т.к. в этом виджете можно редактировать текст, то будем считать, что пользователь либо
        #  выбрал БД через диалоговое окно или вписал путь самостоятельно
        file.write(str(res))
        file.close()
        self.ItSaveLabel.setText('Сохранено!')

    def choice_db(self):
        fname = QFileDialog.getOpenFileName(self, 'Выбрать базу данных', '',
                                            'База данных (*.sqlite);;Все файлы (*)')[0]
        if fname:
            self.DBText.setPlainText(fname)
        self.ItSaveLabel.setText('')
        # эта функция открывает диалоговое окно для выбора БД


if __name__ == '__main__':
    app = QApplication(sys.argv)
    prog = SettingsWindow()
    prog.show()
    sys.exit(app.exec_())
