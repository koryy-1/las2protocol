from PyQt5.QtWidgets import QFormLayout, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QFileDialog, QCheckBox
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
import lasio

from process_sample import calculate_smoothed_data, save2doc

from plot_creator import create_graph_on_canvas

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
        self.cut_button.clicked.connect(self.crop_graphs)

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
        self.success_label = QLabel("")
        params_layout.addWidget(self.success_label)

        # self.save_excel_button
        # las.to_excel('output.xlsx')

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

    def calc_data(self):
        self.smoothed_RSD, self.smoothed_RLD = calculate_smoothed_data(
            self.las, 
            int(self.size_entry.text()), 
            int(self.smooth_count_entry.text())
        )
        self.RLD_on_RSD = np.divide(self.smoothed_RLD, self.smoothed_RSD)
        delta_len = len(self.las["MT"]) - len(self.smoothed_RSD)
        # padded_smoothed_RSD = np.pad(smoothed_RSD, (delta_len, 0), mode='constant')
        self.TEMPER = self.las["MT"][delta_len:]
        self.TIME = self.las["TIME"][delta_len:]

    def crop_data(self):
        self.smoothed_RSD = self.smoothed_RSD[self.move_x:]
        self.smoothed_RLD = self.smoothed_RLD[self.move_x:]
        self.RLD_on_RSD = self.RLD_on_RSD[self.move_x:]
        self.TEMPER = self.TEMPER[self.move_x:]
        self.TIME = self.TIME[self.move_x:]


    def update_red_line_label(self, line_pos_x):
        RSD_Y = int(np.round(self.smoothed_RSD[line_pos_x]))
        RLD_Y = int(np.round(self.smoothed_RLD[line_pos_x]))
        RLD_RSD_Y = np.round(self.RLD_on_RSD[line_pos_x], 3)
        TEMPER_Y = int(self.TEMPER[line_pos_x])
        self.red_line_label_y.setText(f'\tRSD Y: {RSD_Y}\tRLD Y: {RLD_Y}\tRLD/RSD Y: {RLD_RSD_Y}\tTEMPER Y: {TEMPER_Y}')

    def ensure_red_line_created(self):
        if len(self.red_line) == 0:
            for ax in self.axes:
                self.red_line.append(ax.axvline(0, color='red'))

    def draw_red_line(self):
        for i, ax in enumerate(self.axes):
            self.red_line[i].remove()
            self.red_line[i] = ax.axvline(self.move_x, color='red')
        self.canvas.draw()

    def update_red_line(self, new_value):
        if self.axes is None:
            return
        
        if len(self.smoothed_RSD) < new_value:
            new_value = len(self.smoothed_RSD)

        if new_value < 0:
            new_value = 0
        
        self.move_x = new_value
        
        self.update_red_line_label(self.move_x)

        self.draw_red_line()


    def plot_graphs(self):
        if self.las is None:
            return
        
        self.ensure_figure_created()
        self.ensure_red_line_created()
        
        self.clear_graphs()
        
        self.calc_data()

        create_graph_on_canvas(self.axes[0], self.TIME, self.smoothed_RSD, "RSD_1")
        create_graph_on_canvas(self.axes[1], self.TIME, self.smoothed_RLD, "RLD_1")
        create_graph_on_canvas(self.axes[2], self.TIME, self.RLD_on_RSD, "RLD/RSD")
        create_graph_on_canvas(self.axes[3], self.TIME, self.TEMPER, "TEMPER")

        self.x_red_line_spinbox.setMaximum(len(self.smoothed_RSD) - 1)
        self.x_red_line_spinbox.setValue(0)
        if self.move_x == 0:
            self.draw_red_line()

        self.canvas.draw()
        
    def crop_graphs(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data()

        create_graph_on_canvas(self.axes[0], self.TIME, self.smoothed_RSD, "RSD_1")
        create_graph_on_canvas(self.axes[1], self.TIME, self.smoothed_RLD, "RLD_1")
        create_graph_on_canvas(self.axes[2], self.TIME, self.RLD_on_RSD, "RLD/RSD")
        create_graph_on_canvas(self.axes[3], self.TIME, self.TEMPER, "TEMPER")

        self.x_red_line_spinbox.setMaximum(len(self.smoothed_RSD) - 1)
        self.x_red_line_spinbox.setValue(0)
        if self.move_x == 0:
            self.draw_red_line()

        self.canvas.draw()
        
    
    def save_to_docx(self):
        if self.las is None:
            return

        self.success_label.setText("processing...")

        serial_number = self.las.well["SNUM"].value
        date = self.las.well["DATE"].value
        instrument_name = self.las.well["NAME"].value

        description = (serial_number, date, instrument_name)

        # 2 tuples
        data = self.smoothed_RSD, self.smoothed_RLD, self.RLD_on_RSD, self.TEMPER, self.TIME

        thresholds = self.las["THLDS"][0], self.las["THLDL"][0]

        success = save2doc(
            int(self.size_entry.text()),
            bool(self.process_heat_checkbox.isChecked()),
            bool(self.process_cool_checkbox.isChecked()),
            int(self.smooth_count_entry.text()),
            description,
            data,
            thresholds
        )

        if success:
            self.success_label.setText("docx saved successfully")
        else:
            self.success_label.setText("ERROR: failed to save docx")


    def show_calculations(self):
        # Здесь вы можете добавить код для отображения расчетов
        pass
