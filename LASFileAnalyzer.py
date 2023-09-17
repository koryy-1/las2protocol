from PyQt5.QtWidgets import QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import lasio

from process_sample import calculate_smoothed_data, save2doc

from plot_creator import create_plot_on_canvas

class LASFileAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LAS File Analyzer")

        # Создаем главный виджет
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Создаем вертикальный макет для параметров
        params_layout = QVBoxLayout()
        params_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Размер окна
        DURATION_1_COUNT = 4000
        self.size_entry = QLineEdit()
        self.size_entry.setText(str(int(4 * 60 * 1000 / DURATION_1_COUNT)))
        # Количество применений функции сглаживания
        self.smooth_count_entry = QLineEdit()
        self.smooth_count_entry.setText("3")
        # Часть графика для обработки
        self.process_heat_checkbox = QCheckBox("Нагрев")
        self.process_heat_checkbox.setChecked(True)
        self.process_cool_checkbox = QCheckBox("Охлаждение")
        self.process_cool_checkbox.setChecked(True)

        # Создаем виджет для параметров с использованием QFormLayout
        form_layout = QFormLayout()
        form_layout.addRow("Размер окна:", self.size_entry)
        form_layout.addRow("Количество применений сглаживания:", self.smooth_count_entry)
        form_layout.addRow("Какую часть графика обрабатывать:", self.process_heat_checkbox)
        form_layout.addRow("", self.process_cool_checkbox)
        params_layout.addLayout(form_layout)


        # Кнопка открытия .las файла
        self.open_button = QPushButton("Открыть .las файл")
        self.open_button.clicked.connect(self.open_las_file)
        params_layout.addWidget(self.open_button)

        # Метка для вывода пути до файла
        self.file_path_label = QLabel("")
        params_layout.addWidget(self.file_path_label)

        # Кнопка построения графиков
        self.plot_button = QPushButton("Построить графики")
        self.plot_button.clicked.connect(self.plot_graphs)
        params_layout.addWidget(self.plot_button)

        # Создаем виджет Matplotlib для вывода графиков
        self.canvas = FigureCanvas(Figure(figsize=(8, 2 * 4)))
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.canvas)

		# Кнопка показать расчеты
        self.show_calculations_button = QPushButton("Показать расчеты")
        self.show_calculations_button.clicked.connect(self.show_calculations)
        params_layout.addWidget(self.show_calculations_button)

        # Кнопка сохранения в .docx файл
        self.save_button = QPushButton("Сохранить в .docx файл")
        self.save_button.clicked.connect(self.save_to_docx)
        params_layout.addWidget(self.save_button)


        # Создаем главный горизонтальный макет для размещения виджета с параметрами и виджета с графиками
        main_layout = QHBoxLayout()
        main_layout.addLayout(params_layout)
        main_layout.addLayout(graph_layout)

        # Устанавливаем главный макет в главный виджет
        main_widget.setLayout(main_layout)

        self.las = None


    def open_las_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть .las файл", "", "LAS Files (*.las)", options=options)
        if file_path:
            # Здесь вы можете добавить код для обработки выбранного .las файла
            self.file_path_label.setText(file_path.split("/")[-1])
            self.las = lasio.read(file_path, encoding="cp1251")
            pass

    def plot_graphs(self):
        if self.las:
            num_graphs = 4
            fig, axes = plt.subplots(num_graphs, 1, figsize=(8, 2))
            plt.grid(True)

            smoothed_RSD, smoothed_RLD = calculate_smoothed_data(self.las, int(self.size_entry.text()), int(self.smooth_count_entry.text()))


            # Заглушки для данных и обрезания графиков
            create_plot_on_canvas(axes[0], self.las["TIME"], smoothed_RSD, "RSD_1")

            create_plot_on_canvas(axes[1], self.las["TIME"], smoothed_RLD, "RLD_1")

            RLD_on_RSD = smoothed_RLD / smoothed_RSD
            create_plot_on_canvas(axes[2], self.las["TIME"], RLD_on_RSD, "RLD/RSD")

            create_plot_on_canvas(axes[3], self.las["TIME"], self.las["MT"], "TEMPER")


            # Вывод графиков на виджет Matplotlib
            self.canvas.figure = fig
            self.canvas.draw()
    
    def save_to_docx(self):
        if self.las:
            save2doc(
                int(self.size_entry.text()),
                bool(self.process_heat_checkbox.isChecked()),
                bool(self.process_cool_checkbox.isChecked()),
                int(self.smooth_count_entry.text()),
                self.las
            )

    def show_calculations(self):
        # Здесь вы можете добавить код для отображения расчетов
        pass
