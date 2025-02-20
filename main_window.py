#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pickle
import _pickle
import time
import os
import re
from datetime import date
from decimal import Decimal
from typing import List, Any

from PyQt5 import QtCore, QtWidgets, QtGui
import my_form


# метод для заставки
def load_data(sp):
    for i in range(1, 6):  # Имитируем процесс
        time.sleep(1)  # Что-то загружаем
        sp.showMessage("Загрузка данных... {0}%".format(i * 20), QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom,
                       QtCore.Qt.yellow)  # надпись внизу картинки якобы считает ппроценты загрузки
        QtWidgets.qApp.processEvents()  # Запускаем оборот цикла


def load_data_file(a):
    f = open('save_dates/' + a, 'rb')  # открываем файл
    b = pickle.load(f)  # загружаем файл в словарь
    f.close()  # закрываем файл
    return b


def save_data_files(a, b):
    f = open('save_dates/' + a, 'wb')
    pickle.dump(b, f)
    f.close()


def create_dialog_message(a, b, c):
    QtWidgets.QMessageBox.information(a, b, c, defaultButton=QtWidgets.QMessageBox.Ok)


def name_file_comboBox(a: str):
    names_files_list = os.listdir(a)
    name_file = []
    for i in range(len(names_files_list)):
        if re.search('\d+', names_files_list[i]) is not None:
            name_file.append(names_files_list[i][:-4])
    name_file.sort()
    return name_file


class MyWindow(QtWidgets.QMainWindow, my_form.Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.tariffsList = []  # для временного хранения списка тарифов
        self.current_index = None  # для хранения выбранного индекса comboBox
        self.settingTariffDict = {}  # для хранения настроек тарифов
        self.f_salary_dict = {}
        self.payOut_dict = {}

        # настройка dateEdit
        self.date_shift = date  # экземпляр QDate
        self.dateEdit_shifts.setDate(self.date_shift.today())  # устанавливаем текущую дату в editDate

        # вертикальный HeaderList в таблице смен
        self.shiftVerticalHeaderList = ('Яндекс', 'Gett', 'City', 'Штрафы', 'Аванс', 'Общий накат', 'Тариф',
                                        'Мой процент', 'За смену', 'Выплата')
        self.dateMonth = {}  # словарь для хранения данных по сменам за месяц

        # настройка comboBox
        self.tariff_ComboBox_model = QtCore.QStringListModel()  # модель для comboBox
        self.comboBox_setting.setModel(self.tariff_ComboBox_model)  # настраиваем модель для comboBox

        # подготовка таблицы для настройки тарифов
        self.table_settingTariffsModel = QtGui.QStandardItemModel()  # модель для талицы настроек тарифов
        self.tableView_setting.setModel(self.table_settingTariffsModel)  # подключаем модель к таблице
        self.tableHeaderList = ['Накат', 'Проц.']  # список названий колонок
        self.table_settingTariffsModel.setHorizontalHeaderLabels(self.tableHeaderList)  # подключаем названия колонок
        # к таблице

        # настраиваем табдицу смен
        self.StIM_shiftsTable = QtGui.QStandardItemModel()  # модель для талицы смен
        self.StIM_shiftsTable.setVerticalHeaderLabels(self.shiftVerticalHeaderList)  # подключаем лист с названиями
        # строк к таблице
        self.tableView_shifts.setModel(self.StIM_shiftsTable)  # подключаем модель к таблице

        # если файлы, с сохранёнными настройками, существуют то они загружаются для дальнейшего использования
        try:
            self.settingTariffDict = load_data_file('settingTariffDict.txt')  # открываем файл с настройками тарифа
            print('настройки тарифов', self.settingTariffDict)
            self.current_index = load_data_file('comboBox_currentIndex.txt')  # открываем файл с настройкой
            print('выбранный тариф', self.current_index)
            # выбранного тарифа
        # если  файлов с настпройками тарифов нет, то выполняется этот код
        except (FileNotFoundError, EOFError):
            # диалоговое окно с информацией о отсутствии настроеных тарифов
            create_dialog_message(splash, 'Тарифы не настроены!', 'Вам нужно настроить тарифы для расчёта зарплаты.')
        # если тарифы настроены то выполняется этот код
        else:
            self.comboBox_setting.addItems(self.settingTariffDict.keys())  # заполнение comboBox названиями тарифов
            self.comboBox_setting.setCurrentIndex(self.current_index)  # настойка ранее выбраного тарифа
            tariff_dict = self.settingTariffDict[self.comboBox_setting.currentText()]  # выбор соответствующих данных

            # по выбраному тарифу заполняется таблица настроек тарифов
            tariff_keys = list(tariff_dict.keys())  # список для ключей
            tariff_list: List[Any] = list(tariff_dict.values())  # список для настроек тарифов
            for row in range(len(tariff_dict)):  # цикл для заполнения таблицы
                if type(tariff_list[row]) == list:
                    percent_list = ''
                    percent_list_final = ''
                    for j in range(len(tariff_list[row])):
                        percent = str(tariff_list[row][j] * 100)
                        percent_list += percent + ' / '
                        percent_list_final = percent_list[:-3]
                    item_l0 = QtGui.QStandardItem(str(tariff_keys[row]))
                    item_l1 = QtGui.QStandardItem(percent_list_final)
                    self.table_settingTariffsModel.setItem(row, 0, item_l0)
                    self.table_settingTariffsModel.setItem(row, 1, item_l1)
                else:
                    item_0 = QtGui.QStandardItem(str(tariff_keys[row]))  # модель для заполнения первой колонки
                    item_1 = QtGui.QStandardItem(str(tariff_list[row] * 100))  # модель для заполнения
                    # второй колонки
                    self.table_settingTariffsModel.setItem(row, 0, item_0)  # заполняем первую колонки
                    self.table_settingTariffsModel.setItem(row, 1, item_1)  # заполняем вторую колонку

        # загружаем данные смен из сохранённого файла dateMont
        try:
            self.dateMonth = load_data_file(self.dateEdit_shifts.text()[3:] + '.txt')  # открываем файл со сменами
            # текущего месяца
            print('текущий месяц', self.dateMonth)
        # если файла не существует выполняется этот код
        except(FileNotFoundError, EOFError):
            # диалоговое окно с информацией о отсутствии смен в текущем месяце
            create_dialog_message(splash, 'Нет смен в текущем месяце.', 'Создайте смены или загрузите другой месяц.')
        # если файл существует то заполняем таблицу смен
        except _pickle.UnpicklingError:
            create_dialog_message(splash, 'Файл повреждён!!!', 'Требуется восстановление файла')
        else:
            shiftsNameList = list(self.dateMonth.keys())  # список названий смен
            self.StIM_shiftsTable.setHorizontalHeaderLabels(shiftsNameList)  # список горизонтальных заголовков
            index = QtCore.QModelIndex()  # просто индекс
            date_list = []  # список для временного хранения данных по сменам
            for key_dateMonth in self.dateMonth.keys():  # цикл для заполнения списка данных по сменам
                date_list.append(self.dateMonth[key_dateMonth])  # заполняем список с данными по сменам
            for j in range(self.StIM_shiftsTable.columnCount(index)):  # цикл по колонкам
                for row in range(self.StIM_shiftsTable.rowCount(index)):  # цикл по строкам
                    self.StIM_shiftsTable.setItem(row, j, QtGui.QStandardItem(date_list[j][row]))  # заполнение таблицы
                    # данными по сменам

        try:
            self.f_salary_dict = load_data_file('f_salary_dict.txt')
            print('список зарплат', self.f_salary_dict)
            self.payOut_dict = load_data_file('payOut_dict.txt')
            print('список выплат', self.payOut_dict)

        except(FileNotFoundError, EOFError):
            # диалоговое окно с информацией о отсутствии смен в текущем месяце
            create_dialog_message(splash, 'Нет сохранённых данных.', 'При работе программы будут созданны базы данных.')
        else:
            #
            salary_list = []
            payOut_list = []
            key_dateMonth: str
            for key_dateMonth in self.dateMonth.keys():
                salary_list.append(Decimal(self.dateMonth[key_dateMonth][8]))
                payOut_list.append(Decimal(self.dateMonth[key_dateMonth][9]))
            f_salary_dict = dict(zip(list(self.dateMonth.keys()), salary_list))
            self.f_salary_dict.update(f_salary_dict)
            payOut_dict = dict(zip(list(self.dateMonth.keys()), payOut_list))
            self.payOut_dict.update(payOut_dict)
            f_salary = sum(self.f_salary_dict.values())
            payOut = sum(self.payOut_dict.values())
            self.label_debt.setText(str(f_salary - payOut))
            self.label_salary.setText(str(f_salary))
            self.label_payOut.setText(str(payOut))

            name_file = name_file_comboBox('save_dates')
            self.comboBox_selectedMont.addItems(name_file)

        # действие при выборе тарифа
        self.comboBox_setting.activated[str].connect(self.comboBox_setting_activated)  # смена тарифа в comboBox
        # действия меню
        self.comboBox_selectedMont.activated[str].connect(self.comboBox_selectedMonth_activated)
        self.action_addTariff.triggered.connect(self.add_new_tariff)  # добавляет тариф
        self.action_removeTariff.triggered.connect(self.remove_tariff)  # удаляет тариф
        self.action_addRow.triggered.connect(self.tableTariff_addRow)  # добавляет строку в таблицу
        self.action_removeRow.triggered.connect(self.tableTariff_removeRow)  # удаляет строку из таблицы
        self.action_saveTariff.triggered.connect(self.tableTariff_saveTariff)  # сожраняет настройки тарифов в словарь
        self.action_saveSettings.triggered.connect(self.saveSettings)  # сохранят настройки тарифов и программы
        self.action_addShift.triggered.connect(self.addShift_tableShifts)  # добавляем смену
        self.action_calculationShift.triggered.connect(self.calculatedShift)  # расчитываем смену
        self.action_saveData.triggered.connect(self.save_dates)  # сохраняем данные по сменам
        self.action_removeShift.triggered.connect(self.removeShift_tableShifts)  # удаляем смену
        self.pushButton_calcDept.clicked.connect(self.calculate_dept)
        self.action_addMonth.triggered.connect(self.add_month)

    # метод добавляет новый тариф в comboBox
    def add_new_tariff(self):
        self.comboBox_setting.blockSignals(True)
        self.comboBox_setting.setEditable(True)  # разрешение на редактирование
        self.comboBox_setting.setEditText('Новый тариф')  # добавляем "Новый тариф"

    # метод удаляет тариф
    def remove_tariff(self):
        ind = self.comboBox_setting.currentIndex()  # индекс выбранного тарифа
        if self.comboBox_setting.currentText() in self.settingTariffDict:  # если название тарифа есть в списке то
            del self.settingTariffDict[self.comboBox_setting.currentText()]  # удаляем тариф из списка
        self.comboBox_setting.removeItem(ind)  # удаляем название тарифа из comboBox

    # метод добавляет строку в таблицу настроек тарифов
    def tableTariff_addRow(self):
        L = []
        for i in range(0, 2):
            L.append(QtGui.QStandardItem('0'))
        self.table_settingTariffsModel.appendRow(L)

    # метод удаляет выбранную строку из таблицы настроек тарифов
    def tableTariff_removeRow(self):
        ind_remove = self.tableViewSetting.currentIndex()
        if ind_remove.isValid():
            self.table_settingTariffsModel.removeRow(ind_remove.row())

    # метод сохраняет настройки тарифа в settingTariffDict
    def tableTariff_saveTariff(self):
        key_list = []
        date_list = []
        name_tariff = self.comboBox_setting.currentText()
        settingDateDict = {}
        ind = QtCore.QModelIndex()
        for i in range(0, self.table_settingTariffsModel.rowCount(ind)):
            if '/' in self.table_settingTariffsModel.index(i, 1).data():
                percent_list = str(self.table_settingTariffsModel.index(i, 1).data()).split(sep='/')
                percent_list[0] = Decimal(percent_list[0].replace(',', '.')) / Decimal(100)
                percent_list[1] = Decimal(percent_list[1].replace(',', '.')) / Decimal(100)
                settingDateDict[self.table_settingTariffsModel.index(i, 0).data()] = percent_list
            else:
                date_list.append(Decimal(str(self.table_settingTariffsModel.index(i, 1).data()).replace(',', '.')) /
                                 Decimal(100))
                key_list.append(str(self.table_settingTariffsModel.index(i, 0).data()))
        settingDateDict1 = dict(zip(key_list, date_list))
        settingDateDict1.update(settingDateDict)
        self.settingTariffDict.update({name_tariff: settingDateDict1})
        self.comboBox_setting.blockSignals(False)
        return self.settingTariffDict

    # метод сохраняет настройки тарифов в файлы
    def saveSettings(self):
        save_data_files('settingTariffDict.txt', self.settingTariffDict)
        save_data_files('comboBox_currentIndex.txt', self.comboBox_setting.currentIndex())

    # метод активирует выбранный тариф и показывает его настройки
    def comboBox_setting_activated(self, v):
        print(v)
        if v in self.settingTariffDict:
            #
            tariff_dict = self.settingTariffDict[v]
            #
            tariff_keys = list(tariff_dict.keys())
            tariff_list = list(tariff_dict.values())
            #
            for row in range(len(tariff_dict)):
                if type(tariff_list[row]) == list:
                    percent_list = ''
                    percent_list_final = ''
                    for j in range(len(tariff_list[row])):
                        percent = str(tariff_list[row][j] * 100)
                        percent_list += percent + ' / '
                        percent_list_final = percent_list[:-3].replace('.', ',')
                    item_l0 = QtGui.QStandardItem(str(tariff_keys[row]))
                    item_l1 = QtGui.QStandardItem(percent_list_final)
                    self.table_settingTariffsModel.setItem(row, 0, item_l0)
                    self.table_settingTariffsModel.setItem(row, 1, item_l1)
                else:
                    item_0 = QtGui.QStandardItem(str(tariff_keys[row]))
                    item_1 = QtGui.QStandardItem(str(tariff_list[row] * 100).replace('.', ','))
                    self.table_settingTariffsModel.setItem(row, 0, item_0)
                    self.table_settingTariffsModel.setItem(row, 1, item_1)

            ind = self.tableView_shifts.currentIndex()
            sel = self.tableView_shifts.selectionModel()

            if sel.isColumnSelected(ind.column(), QtCore.QModelIndex()):
                self.StIM_shiftsTable.setItem(6, ind.column(), QtGui.QStandardItem(self.comboBox_setting.currentText()))

    def comboBox_selectedMonth_activated(self, v):
        try:
            self.dateMonth = load_data_file(v)
            print('выбранный месяц', self.dateMonth)
        except(FileNotFoundError, EOFError):
            # диалоговое окно с информацией о отсутствии смен в текущем месяце
            create_dialog_message(splash, 'Нет смен в выбраном месяце.', 'Попробуйте выбрать другой месяц.')
            # если файл существует то заполняем таблицу смен
        except _pickle.UnpicklingError:
            create_dialog_message(splash, 'Файл повреждён!!!', 'Требуется восстановление файла')
        else:
            index = QtCore.QModelIndex()  # просто индекс
            self.StIM_shiftsTable.removeColumns(0, self.StIM_shiftsTable.columnCount(index), parent=index)
            shiftsNameList = list(self.dateMonth.keys())  # список названий смен
            self.StIM_shiftsTable.setHorizontalHeaderLabels(shiftsNameList)  # список горизонтальных заголовков
            date_list = []  # список для временного хранения данных по сменам
            for key_dateMonth in self.dateMonth.keys():  # цикл для заполнения списка данных по сменам
                date_list.append(self.dateMonth[key_dateMonth])  # заполняем список с данными по сменам
            for j in range(self.StIM_shiftsTable.columnCount(index)):  # цикл по колонкам
                for row in range(self.StIM_shiftsTable.rowCount(index)):  # цикл по строкам
                    self.StIM_shiftsTable.setItem(row, j, QtGui.QStandardItem(date_list[j][row]))  # заполнение таблицы
                    # данными по сменам
            self.dateEdit_shifts.setDate(self.date_shift.today().replace(month=int(self.comboBox_selectedMont.
                                                                                   currentText()[:-3])))

    def add_month(self):
        index = QtCore.QModelIndex()  # просто индекс
        self.StIM_shiftsTable.removeColumns(0, self.StIM_shiftsTable.columnCount(index), parent=index)
        self.dateMonth = {}
        save_data_files(self.dateEdit_shifts.text()[3:] + '.txt', self.dateMonth)
        name_file = name_file_comboBox('save_dates')
        self.comboBox_selectedMont.clear()
        self.comboBox_selectedMont.addItems(name_file)

    def remove_month(self):
        pass

    # метод добавлят смену в таблицу
    def addShift_tableShifts(self):
        list_row = []
        for i in range(0, 9):
            list_row.append(QtGui.QStandardItem('0'))
        list_row.insert(6, QtGui.QStandardItem(self.comboBox_setting.currentText()))
        self.StIM_shiftsTable.appendColumn(list_row)
        index = QtCore.QModelIndex()
        self.StIM_shiftsTable.setHorizontalHeaderItem(self.StIM_shiftsTable.columnCount(index) - 1,
                                                      QtGui.QStandardItem(self.dateEdit_shifts.text()))

    #
    def removeShift_tableShifts(self):
        index = self.tableView_shifts.currentIndex()
        if index.isValid():
            self.StIM_shiftsTable.removeColumn(index.column())

    # метод расчитывает смену
    def calculatedShift(self):
        coefficient = 0
        key_reverse_dict = ''
        ind = self.tableView_shifts.currentIndex()
        sel = self.tableView_shifts.selectionModel()

        if sel.isColumnSelected(ind.column(), QtCore.QModelIndex()):
            fullSalary = sum([Decimal(self.StIM_shiftsTable.index(0, ind.column()).data(role=0)),
                              Decimal(self.StIM_shiftsTable.index(1, ind.column()).data(role=0)),
                              Decimal(self.StIM_shiftsTable.index(2, ind.column()).data(role=0))])
            self.StIM_shiftsTable.setItem(5, ind.column(), QtGui.QStandardItem(str(fullSalary)))
            reverse_dict = self.settingTariffDict[self.comboBox_setting.currentText()]
            for key_reverse_dict in sorted(reverse_dict, reverse=True):
                if Decimal(fullSalary) >= Decimal(key_reverse_dict):
                    coefficient = reverse_dict[key_reverse_dict]
                    break

            if type(coefficient) == list:
                over_plan = fullSalary - Decimal(key_reverse_dict)
                my_percent = Decimal(key_reverse_dict) * coefficient[0] + over_plan * coefficient[1]
                self.StIM_shiftsTable.setItem(7, ind.column(), QtGui.QStandardItem(str(my_percent)))
            else:
                my_percent = Decimal(fullSalary) * Decimal(coefficient)
                self.StIM_shiftsTable.setItem(7, ind.column(), QtGui.QStandardItem(str(my_percent)))
            my_salary = my_percent - Decimal(self.StIM_shiftsTable.index(3, ind.column()).data(role=0)) - \
                        Decimal(self.StIM_shiftsTable.index(4, ind.column()).data(role=0))
            self.StIM_shiftsTable.setItem(8, ind.column(), QtGui.QStandardItem(str(my_salary)))
            self.StIM_shiftsTable.setItem(6, ind.column(), QtGui.QStandardItem(self.comboBox_setting.currentText()))

            self.f_salary_dict[self.StIM_shiftsTable.horizontalHeaderItem(ind.column()).data(role=0)] = my_salary
            self.payOut_dict[self.StIM_shiftsTable.horizontalHeaderItem(ind.column()).data(role=0)] = \
                Decimal(self.StIM_shiftsTable.item(9, ind.column()).data(role=0))
            f_salary = sum(self.f_salary_dict.values())
            payOut = sum(self.payOut_dict.values())
            self.label_debt.setText(str(f_salary - payOut))
            self.label_salary.setText(str(f_salary))
            self.label_payOut.setText(str(payOut))
        else:
            QtWidgets.QMessageBox.information(splash, "Предупреждение",
                                              "Пожалуйста выберите смену для расчёта",
                                              buttons=QtWidgets.QMessageBox.Close,
                                              defaultButton=QtWidgets.QMessageBox.Close)

    def calculate_dept(self):
        ind_sum = QtCore.QModelIndex()
        shift_name_list = []
        f_salary_list = []
        payOut_list = []
        for i in range(self.StIM_shiftsTable.columnCount(ind_sum)):
            shift_name_list.append(self.StIM_shiftsTable.horizontalHeaderItem(i).data(role=0))
            f_salary_list.append(Decimal(self.StIM_shiftsTable.index(8, i).data(role=0)))
            payOut_list.append(Decimal(self.StIM_shiftsTable.index(9, i).data(role=0)))
        self.f_salary_dict.update(dict(zip(shift_name_list, f_salary_list)))
        self.payOut_dict.update(dict(zip(shift_name_list, payOut_list)))
        f_salary = sum(list(self.f_salary_dict.values()))
        pay_Out = sum(list(self.payOut_dict.values()))
        self.label_debt.setText(str(f_salary - pay_Out))
        self.label_salary.setText(str(f_salary))
        self.label_payOut.setText(str(pay_Out))

    def save_dates(self):
        index = QtCore.QModelIndex()
        date_shifts = []
        shift_name_list = []
        for j in range(self.StIM_shiftsTable.columnCount(index)):
            shift_name_list.append(self.StIM_shiftsTable.horizontalHeaderItem(j).text())

        for j in range(self.StIM_shiftsTable.columnCount(index)):
            date_shift = []
            for i in range(self.StIM_shiftsTable.rowCount(index)):
                date_shift.append(self.StIM_shiftsTable.index(i, j).data())
            date_shifts.append(date_shift)
        self.dateMonth = dict(zip(shift_name_list, date_shifts))

        save_data_files(self.dateEdit_shifts.text()[3:] + '.txt', self.dateMonth)
        save_data_files('f_salary_dict.txt', self.f_salary_dict)
        save_data_files('payOut_dict.txt', self.payOut_dict)

        name_file = name_file_comboBox('save_dates')
        self.comboBox_selectedMont.clear()
        self.comboBox_selectedMont.addItems(name_file)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(QtGui.QPixmap("data/yandex_taxi.png"))
    font = QtGui.QFont()
    font.setFamily("C059 [UKWN]")
    font.setPointSize(24)
    font.setBold(True)
    font.setItalic(True)
    font.setWeight(75)
    splash.setFont(font)
    splash.showMessage("Загрузка данных... 0%", QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom, QtCore.Qt.yellow)
    splash.show()  # Отображаем заставку
    QtWidgets.qApp.processEvents()  # Запускаем оборот цикла
    window = MyWindow()  # Создаем экземпляр класса
    desktop = QtWidgets.QApplication.desktop()
    window.move(desktop.availableGeometry().center() - window.rect().center())
    ico = QtGui.QIcon('data/taxi_icon_48.png')
    window.setWindowIcon(ico)
    load_data(splash)  # Загружаем данные
    window.show()  # Отображаем окно
    splash.finish(window)  # Скрываем заставку
    sys.exit(app.exec_())  # Запускаем цикл обработки событий
