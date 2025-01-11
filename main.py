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
        self.titles = ['ID', 'Сорт', 'Степень обжарки', 'Форма', 'Описание', 'Цена', 'Объём упаковки']
        self.btn.clicked.connect(self.show_info)
        self.add.clicked.connect(lambda checked, text=self.add.text(): self.add_edit(text))
        self.edit.clicked.connect(lambda checked, text=self.edit.text(): self.add_edit(text))

    def show_info(self):
        res = self.cur.execute("SELECT * FROM coffee").fetchall()
        self.table.setColumnCount(len(self.titles))
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(self.titles)
        for i, row in enumerate(res):
            self.table.setRowCount(i + 1)
            for j, item in enumerate(row):
                if j == 1:
                    res = self.cur.execute("SELECT name FROM sorts WHERE id=?", (int(item),)).fetchall()
                    item = res[0][0]
                self.table.setItem(i, j, QTableWidgetItem(str(item)))
        self.table.resizeColumnsToContents()

    def add_edit(self, text):
        self.statusBar().showMessage('')
        if len(self.table.selectedItems()) == 0 and text == 'Отредактировать':
            self.statusBar().showMessage('Не выбран элемент')
        elif len(self.table.selectedItems()) > 0 and text == 'Отредактировать':
            id = int(self.table.item(self.table.selectedItems()[0].row(), 0).text())
            wind = AddEditView(self, id)
            wind.show()
        else:
            wind = AddEditView(self)
            wind.show()


class AddEditView(QMainWindow):
    def __init__(self, parent=None, coffee_id=None):
        super().__init__(parent)
        self.con = sqlite3.connect('coffee.sqlite')
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.coffee_id = coffee_id
        self.par = parent
        if coffee_id is None:
            self.result.setText('Добавить')
            self.result.clicked.connect(lambda checked: self.verdict(0))
        else:
            self.result.setText('Отредактировать')
            self.result.clicked.connect(lambda checked: self.verdict(1))
            self.load_info()

    def verdict(self, zn):
        self.statusBar().showMessage('')
        cur = self.con.cursor()
        try:
            name = self.sort.text()
            price = int(self.price.text())
            value = int(self.value.text())
            desc = self.desc.toPlainText()
            roast = self.roast.text()
            form = self.form.text()
            if not name:
                raise ValueError
            res = cur.execute("SELECT * FROM sorts WHERE name=?", (self.sort.text(),)).fetchone()
            if res is None:
                cur.execute("INSERT INTO sorts (name) VALUES (?)", (name,))
                self.con.commit()
            if not desc or not form or not roast or not self.sort.text():
                raise ValueError
            sort = cur.execute("SELECT id FROM sorts WHERE name=?", (self.sort.text(),)).fetchone()
            if zn == 0:
                cur.execute("INSERT INTO coffee(sort, roast, form, description,"
                            "price, value) VALUES(?,?,?,?,?,?)",
                            (sort[0], roast, form, desc, price, value))
                self.con.commit()
            else:
                cur.execute("UPDATE coffee SET sort=?, roast=?, form=?, description=?, price=?,value=? WHERE id=?",
                            (sort[0], roast, form, desc, price, value, self.coffee_id))
                self.con.commit()
            self.par.show_info()
            self.close()
        except Exception as e:
            print(e)
            self.statusBar().showMessage('Некорректный ввод')

    def load_info(self):
        cur = self.con.cursor()
        self.titles = ['ID', 'Сорт', 'Степень обжарки', 'Форма', 'Описание', 'Цена', 'Объём упаковки']
        res = cur.execute('SELECT * FROM coffee WHERE id=?', (self.coffee_id,)).fetchone()
        sort = cur.execute("SELECT name FROM sorts WHERE id=?", (res[1],)).fetchone()
        self.sort.setText(sort[0])
        self.roast.setText(res[2])
        self.form.setText(res[3])
        self.desc.setPlainText(res[4])
        self.price.setText(str(res[5]))
        self.value.setText(str(res[6]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MyApp()
    win.show()
    sys.exit(app.exec())
