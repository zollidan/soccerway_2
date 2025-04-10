import xlwt
from datetime import datetime

from constants import *

# Создание шапки в EXEL файле
def make_header(worksheet):
    
    x = y = 0
    for label in HEADER_EXEL:
        worksheet.write(x, y, label, STYLE_HEAD)
        y += 1


class ExcelManager():

    def __init__(self, filename=EXEL_NAME, retry_count=MAX_COUNT_REPEAT_EXEL):
        self.wb = xlwt.Workbook()
        self.sheet = self.wb.add_sheet('Data')
        self.row = 0
        self.column = 0
        self.filename = filename
        self.retry = retry_count
        self.make_header()


    def make_header(self):
        # Создание шапки в EXEL файле
        for label in HEADER_EXEL:
            self.write(label, STYLE_HEAD)
        self.next_row()


    def write(self, label, style=xlwt.Style.default_style):
        # Запись в тек. ячейку + переход в следующию
        self.sheet.write(r=self.row, c=self.column, label=label, style=style)
        self.column += 1


    def next_row(self):
        # Переход на след. строку
        self.column = 0
        self.row += 1


    def save(self):
        # Сохраняем файл
        name = self.filename
        k = 1
        for _ in range(self.retry):
            try:
                self.wb.save(name + '.xls')
            except:
                if k >= MAX_COUNT_REPEAT_EXEL:
                    print("!!! Файл не сохранён !!!")
                    break
                name += "_" + str(k)
            else:
                print("[ Файл сохранён:", name + ".xls ]")
                break

