import sqlite3
import sys
from random import randint

from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QFont, QPixmap, QTransform, QColor, QIcon, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QListWidget, QComboBox, QListWidgetItem, \
    QWidget, QLabel, QMessageBox, QDialog, QTextEdit, QTableWidget, QTableWidgetItem, QAbstractItemView, QPlainTextEdit
from PyQt6 import uic


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        con = sqlite3.connect('coffee.sqlite')
        self.cur = con.cursor()
        self.make_par()
        self.titles = ['ID', 'Сорт', 'Степень обжарки', 'Форма', 'Описание', 'Цена', 'Объём упаковки']
        self.btn.clicked.connect(self.show_info)

    def make_par(self):
        self.params = {}
        res = self.cur.execute('SELECT * FROM sorts').fetchall()
        for i, j in res:
            self.params[i] = j

    def show_info(self):
        res = self.cur.execute("SELECT * FROM coffee").fetchall()
        self.table.setColumnCount(len(self.titles))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.titles)
        for i, row in enumerate(res):
            self.table.setRowCount(i + 1)
            for j, item in enumerate(row):
                if j == 1:
                    item = self.params.get(item)
                self.table.setItem(i, j, QTableWidgetItem(str(item)))
        self.table.resizeColumnsToContents()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
