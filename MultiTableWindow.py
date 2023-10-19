from ast import Tuple
import math
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from models.ColumnData import AbstractColumnData

from models.GraphData import GraphData

class MultiTableWindow(QWidget):
    def __init__(self, datas, rows, cols):
        super().__init__()

        self.setWindowTitle('Multiple Tables Example')
        self.setGeometry(100, 100, int((22 + (22 + 418) * cols) * 1.25), int((22 + (50 + 242) * rows) * 1.25))

        row_layout = QHBoxLayout()
        
        for heating_table, cooling_table, column_data in datas:
            col_layout = QVBoxLayout()
            if heating_table is not None:
                table = self.create_table(heating_table, column_data, 'Нагрев')
                col_layout.addWidget(table)
            if cooling_table is not None:
                table = self.create_table(cooling_table, column_data, 'Охлаждение')
                col_layout.addWidget(table)
            row_layout.addLayout(col_layout)

        self.setLayout(row_layout)

    def create_table(self, calc_table, column_data: AbstractColumnData, title):
        table = QTableWidget()
        table.setRowCount(7)
        table.setColumnCount(4)

        table.setHorizontalHeaderLabels(
            [
                'Формула',
                column_data.near_probe, column_data.far_probe,
                f'{column_data.far_probe}/{column_data.near_probe}'
            ]
        )
        # Увеличиваем шрифт для заголовков
        header_font = table.horizontalHeader().font()
        header_font.setPointSize(12)
        table.horizontalHeader().setFont(header_font)

        table.setVerticalHeaderLabels(['1', '2', '3', '4'])
        header_font = table.verticalHeader().font()
        header_font.setPointSize(12)
        table.verticalHeader().setFont(header_font)

        # Заполняем таблицу данными (здесь просто пример с номерами ячеек)
        for i, row in enumerate(calc_table):
            for j, col in enumerate(row[1:]):
                item = QTableWidgetItem(f'{col}')
                table.setItem(i, j, item)

                # Увеличиваем шрифт
                font = item.font()
                font.setPointSize(12)
                item.setFont(font)

        # Устанавливаем жирный шрифт для последних двух строк
        for i in range(table.rowCount() - 2, table.rowCount()):
            for j in range(table.columnCount()):
                item = table.item(i, j)
                font = item.font()
                font.setBold(True)
                item.setFont(font)

        # Добавляем заголовок таблицы
        header_label = QLabel(title)
        font = header_label.font()
        font.setPointSize(12)
        font.setBold(True)
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(header_label)
        layout.addWidget(table)

        container = QWidget()
        container.setLayout(layout)

        return container


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiTableWindow()
    window.show()
    sys.exit(app.exec_())
