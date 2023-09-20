from PyQt5.QtWidgets import QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QFileDialog, QCheckBox
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

        # Создание кнопки "Обрезать"
        self.cut_button = QPushButton("Обрезать")
        self.cut_button.clicked.connect(self.crop_graph)

        # ввод со стрелками
        self.smoothed_RSD = []
        self.smoothed_RLD = []
        self.RLD_on_RSD = []
        self.TEMPER = []
        self.TIME = []
        self.red_line_label_x = QLabel("X: ")
        self.red_line_label_y = QLabel("")
        self.x_red_line_spinbox = QSpinBox(self)
        self.x_red_line_spinbox.setMaximum(2147483647)
        self.x_red_line_spinbox.valueChanged.connect(self.update_red_line)

        # layout for spinbox
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 20, 0)
        spinbox_layout.addWidget(self.red_line_label_x)
        spinbox_layout.addWidget(self.x_red_line_spinbox)
        spinbox_layout.addWidget(self.red_line_label_y)

        btns_layout = QHBoxLayout()
        btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btns_layout.setContentsMargins(20, 0, 0, 0)
        btns_layout.addLayout(spinbox_layout)
        btns_layout.addWidget(self.cut_button)

        # Создаем виджет Matplotlib для вывода графиков
        self.canvas = FigureCanvas(Figure(figsize=(16, 16)))
        # self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        # self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        # self.canvas.mpl_connect('button_release_event', self.on_mouse_release)

        graph_layout = QVBoxLayout()
        graph_layout.addLayout(btns_layout)
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

        self.axes = []

        # Создание красной вертикальной линии
        self.red_line = []
        self.move_x = 0

        self.dragging = False


    def on_mouse_press(self, event):
        if event.button == 1 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.dragging = True

            self.move_x = int(event.xdata)
            self.x_red_line_spinbox.setValue(self.move_x)

    def on_mouse_move(self, event):
        if self.dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.move_x = int(event.xdata)
            self.x_red_line_spinbox.setValue(self.move_x)

    def on_mouse_release(self, event):
        if self.dragging:
            self.dragging = False
            # print("release", int(event.xdata))


    def open_las_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть .las файл", "", "LAS Files (*.las)", options=options)
        if file_path:
            # Здесь вы можете добавить код для обработки выбранного .las файла
            self.file_path_label.setText(file_path.split("/")[-1])
            self.las = lasio.read(file_path, encoding="cp1251")
            
            self.plot_graphs()

    def create_figure(self):
        fig, self.axes = plt.subplots(4, 1, figsize=(8, 6))

        fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)

        self.canvas.figure = fig

    def ensure_figure_created(self):
        if len(self.axes) == 0:
            self.create_figure()

    def clear_graphs(self):
        for ax in self.axes:
            ax.clear()

    def update_graphs(self):
        # Вывод графиков на виджет Matplotlib
        self.ensure_red_line_created()
        
        self.canvas.draw()


    def plot_graphs(self):
        if self.las is None:
            return
        
        self.ensure_figure_created()
        self.ensure_red_line_created()
        
        self.clear_graphs()
        
        self.x_red_line_spinbox.setValue(0)

        self.smoothed_RSD, self.smoothed_RLD = calculate_smoothed_data(self.las, int(self.size_entry.text()), int(self.smooth_count_entry.text()))
        self.RLD_on_RSD = np.divide(self.smoothed_RLD, self.smoothed_RSD)
        delta_len = len(self.las["MT"]) - len(self.smoothed_RSD)
        self.TEMPER = self.las["MT"][delta_len:]
        self.TIME = self.las["TIME"]

        create_plot_on_canvas(self.axes[0], self.TIME, self.smoothed_RSD, "RSD_1")
        create_plot_on_canvas(self.axes[1], self.TIME, self.smoothed_RLD, "RLD_1")
        
        create_plot_on_canvas(self.axes[2], self.TIME, self.RLD_on_RSD, "RLD/RSD")
        create_plot_on_canvas(self.axes[3], self.TIME, self.TEMPER, "TEMPER")

        RSD_Y = int(np.round(self.smoothed_RSD[0]))
        RLD_Y = int(np.round(self.smoothed_RLD[0]))
        RLD_RSD_Y = np.round(self.RLD_on_RSD[0], 3)
        TEMPER_Y = int(self.las["MT"][0])
        self.red_line_label_y.setText(f'RSD Y: {RSD_Y}   RLD Y: {RLD_Y}   RLD/RSD Y: {RLD_RSD_Y}   TEMPER Y: {TEMPER_Y}')

        self.update_graphs()
        
    def crop_graph(self):
        if self.las is None:
            return
        
        num_graphs = 4
        fig, self.axes = plt.subplots(num_graphs, 1, figsize=(8, 6))

        self.smoothed_RSD = self.smoothed_RSD[self.move_x:]
        self.smoothed_RLD = self.smoothed_RLD[self.move_x:]
        self.RLD_on_RSD = self.RLD_on_RSD[self.move_x:]
        self.TEMPER = self.TEMPER[self.move_x:]
        self.TIME = self.TIME[self.move_x:]

        create_plot_on_canvas(self.axes[0], self.TIME, self.smoothed_RSD, "RSD_1")
        create_plot_on_canvas(self.axes[1], self.TIME, self.smoothed_RLD, "RLD_1")
        
        self.RLD_on_RSD = self.smoothed_RLD / self.smoothed_RSD
        create_plot_on_canvas(self.axes[2], self.TIME, self.RLD_on_RSD, "RLD/RSD")
        create_plot_on_canvas(self.axes[3], self.TIME, self.TEMPER, "TEMPER")
        
        self.x_red_line_spinbox.setValue(0)

        self.update_graphs(fig)
        
    def ensure_red_line_created(self):
        if len(self.red_line) == 0 or self.axes is not None:
            for ax in self.axes:
                self.red_line.append(ax.axvline(0, color='red'))

    def update_red_line(self, new_value):
        if self.axes is None:
            return
        
        if len(self.smoothed_RSD) < new_value:
            new_value = len(self.smoothed_RSD) - 1

        if new_value < 0:
            new_value = 0
        
        self.move_x = new_value
        
        RSD_Y = int(np.round(self.smoothed_RSD[self.move_x]))
        RLD_Y = int(np.round(self.smoothed_RLD[self.move_x]))
        RLD_RSD_Y = np.round(self.RLD_on_RSD[self.move_x], 3)
        TEMPER_Y = int(self.las["MT"][self.move_x])
        self.red_line_label_y.setText(f'RSD Y: {RSD_Y}   RLD Y: {RLD_Y}   RLD/RSD Y: {RLD_RSD_Y}   TEMPER Y: {TEMPER_Y}')

        for i, ax in enumerate(self.axes):
            self.red_line[i].remove()
            self.red_line[i] = ax.axvline(self.move_x, color='red')
            # if self.red_line is None:
            #     self.red_line = ax.axvline(self.move_x, color='red')
            # else:
            #     self.red_line.set_xdata(self.move_x)
        self.canvas.draw()

    
    
    def save_to_docx(self):
        if self.las is None:
            return
        
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