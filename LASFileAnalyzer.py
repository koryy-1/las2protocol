from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

from SidePanel import SidePanel
from graph_layout.GraphCanvas import GraphCanvas

class LASFileAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LAS File Analyzer")

        # Создаем главный виджет
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Создаем главный горизонтальный макет для размещения виджета с параметрами и виджета с графиками
        main_layout = QHBoxLayout()
        graph_canvas = GraphCanvas()
        side_panel = SidePanel(self, graph_canvas)
        main_layout.addLayout(side_panel)
        main_layout.addLayout(graph_canvas)

        # Устанавливаем главный макет в главный виджет
        main_widget.setLayout(main_layout)
