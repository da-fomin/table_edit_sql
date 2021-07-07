import datetime as dt
import sqlite3

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFrame


# pd.options.display.expand_frame_repr = False

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактирование в tableWidget и обновление данных в БД с помощью SQL-запроса")
        self.resize(640, 460)

        self.con = sqlite3.connect("data.db")

        self.hns = {}
        self.params = {}

        self.centralWidget = QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(4, 2, 4, 4)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(0, 2, 20, 2)
        self.horizontalLayout_2.setSpacing(10)
        self.comboBox = QtWidgets.QComboBox(self.centralWidget)
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.pushButton = QtWidgets.QPushButton(self.centralWidget)
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralWidget)
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.horizontalLayout_2.setStretch(0, 2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.tableWidget = QtWidgets.QTableWidget(self.centralWidget)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout_2.addWidget(self.tableWidget)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralWidget)

        QtCore.QMetaObject.connectSlotsByName(self)

        self.pushButton.setText(" Выбрать для редактирования ")
        self.pushButton.clicked.connect(self.data_selection)
        self.pushButton.setStyleSheet("background-color: rgb(100, 255, 0);")

        self.pushButton_2.setText(" Просмотр, Дата и Время в одной колонке ")
        self.pushButton_2.clicked.connect(self.data_selection_2)
        self.pushButton_2.setStyleSheet("background-color: rgb(160, 222, 255);")

        self.tableWidget.currentCellChanged.connect(self.action_cell)
        self.type_selection()

    def type_selection(self):
        # Собираем список уникальных "Услуг" для меню comboBox
        for service in self.con.execute("select [Услуга] from Marakuya").fetchall():
            self.params[service[0]] = service[0]
        self.comboBox.addItems(list(self.params.keys()))

    def data_selection(self):  # ORDER BY DESC / ASC (сортировка по убыванию / возрастанию
        # Подключение к БД
        db = sqlite3.connect("data.db")
        # SQL запрос для получения данных с БД
        sql_txt = "SELECT * FROM Marakuya WHERE [Услуга] = '{}' ORDER BY [Дата_Время] ASC".format(
            self.params.get(self.comboBox.currentText()))
        # Заполняем Data Frame данными из БД
        df = pd.read_sql(sql_txt, con=db)
        # Создаем колонки "Дата" и "Время", по данным из колонки "Дата_Время"
        df['Дата'] = pd.to_datetime(df['Дата_Время'], format='%Y-%m-%d').dt.strftime('%d.%m.%Y')
        df['Время'] = pd.to_datetime(df['Дата_Время'], format='%Y-%m-%d').dt.strftime('%H:%M')
        # Удаляем колонку "Дата_Время"
        df.pop('Дата_Время')
        # Пересортировка колонок для вывода
        df = df[['Телефон', 'Дата', 'Время', 'Услуга', 'ФИО_клиента', 'Сумма', 'Комментарий']]

        self.tableWidget.setColumnCount(len(df.columns))
        self.tableWidget.setRowCount(len(df.index))
        self.tableWidget.setHorizontalHeaderLabels(list(df.columns.values))
        # Заполняем таблицу данными
        for i, row in df.iterrows():
            # Добавление строки
            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(row[j])))
                # Выравниваем колонки по содержимому
                self.tableWidget.resizeColumnsToContents()
                # Добавляем рамку для таблицы
                self.tableWidget.setFrameShape(QFrame.WinPanel)
        # Закрываем доступ к БД
        db.close()
        # Очищаем предыдущие данные с history_value
        self.hns.clear()
        self.tableWidget.setEnabled(True)

    def data_selection_2(self):  # ORDER BY DESC / ASC (сортировка по убыванию / возрастанию
        self.tableWidget.clear()
        sql_txt = "SELECT * FROM Marakuya WHERE [Услуга] = '{}' ORDER BY [Дата_Время] ASC".format(
            self.params.get(self.comboBox.currentText()))

        result = self.con.execute(sql_txt).fetchall()

        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))

        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                """Выравнивание таблицы"""
                self.tableWidget.resizeColumnsToContents()
        self.tableWidget.setEnabled(False)

    def action_cell(self):
        if self.tableWidget.isEnabled() and self.tableWidget.currentRow() != -1 and self.tableWidget.currentColumn() != -1:
            # Получаем текущую строку
            row = self.tableWidget.currentRow()
            # Получаем текущую колонку
            column = self.tableWidget.currentColumn()
            # Получаем значение текущей ячейки
            cell_text = self.tableWidget.item(row, column).text()
            # Получаем "Дата" и "Время" с выбранной строки
            cell_date = self.tableWidget.item(row, 1).text()
            cell_time = self.tableWidget.item(row, 2).text()
            # Собираем "Дата_Время"
            cell_date_time = dt.datetime.strptime(f"""{cell_date} {cell_time}""", '%d.%m.%Y %H:%M')
            # Проверяем данные с history_value
            if self.hns.values():
                # Проверяем значение предыдущей ячейки
                current_value = self.tableWidget.item(self.hns['row'], self.hns['column']).text()
                # Получаем значение с history_value
                former_value = self.hns['cell_text']
                # Сравниваем текущее значение с предыдущим, при отличии обновляем в базе
                if former_value != current_value:
                    # Получаем "Дата" и "Время" с предыдущей строки
                    current_date = self.tableWidget.item(self.hns['row'], 1).text()
                    current_time = self.tableWidget.item(self.hns['row'], 2).text()
                    # Собираем "Дата_Время" для предыдущей строки
                    current_date_time = dt.datetime.strptime(f"""{current_date} {current_time}""", '%d.%m.%Y %H:%M')
                    # SQL запрос, для обновления данных в БД
                    sql_txt = f"""UPDATE Marakuya SET 
                                                    [Телефон] = '{self.tableWidget.item(self.hns['row'], 0).text()}', 
                                                    [Дата_Время] = '{current_date_time}',
                                                    [Услуга] = '{self.tableWidget.item(self.hns['row'], 3).text()}', 
                                                    [ФИО_клиента] = '{self.tableWidget.item(self.hns['row'], 4).text()}',
                                                    [Сумма] = '{self.tableWidget.item(self.hns['row'], 5).text()}', 
                                                    [Комментарий] = '{self.tableWidget.item(self.hns['row'], 6).text()}' 
                                              WHERE [Дата_Время] = '{self.hns['Дата_Время']}' 
                                                AND [Телефон] = '{self.hns['Телефон']}';"""
                    # Обновляем данные в БД
                    self.con.executemany(sql_txt, ([],))
                    # Подтверждаем и сохраняем изменения в БД
                    self.con.commit()

            # Сохраняем текущее значение в history_value
            self.history_value('row', row)
            self.history_value('column', column)
            self.history_value('cell_text', cell_text)
            self.history_value('Телефон', self.tableWidget.item(row, 0).text())
            self.history_value('Дата', self.tableWidget.item(row, 1).text())
            self.history_value('Время', self.tableWidget.item(row, 2).text())
            self.history_value('Дата_Время', cell_date_time)

    def history_value(self, key, value):
        self.hns[key] = value


def run_app():
    app = QApplication([])
    mw = MainApp()
    mw.show()
    app.exec()


run_app()
