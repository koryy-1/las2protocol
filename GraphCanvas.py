from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt5.QtCore import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from lasio import LASFile
from typing import Type

from graph_creator import create_graph_on_canvas
from models.ColumnData import AbstractColumnData, ColumnDataGamma, ColumnDataNeutronic
from models.GraphData import GraphData
from utils import smoothing_function

class GraphCanvas(QVBoxLayout):
    def __init__(self):
        super().__init__()

        # Создание кнопки "Обрезать"
        self.cut_button = QPushButton("Обрезать")
        self.cut_button.clicked.connect(self.crop_graphs)

        # ввод со стрелками
        self.red_line_label_x = QLabel("X: ")
        self.red_line_label_y = QLabel("")
        self.x_red_line_spinbox = QSpinBox()
        self.x_red_line_spinbox.setMaximum(2147483647)
        self.x_red_line_spinbox.valueChanged.connect(self.update_red_line)

        # layout for spinbox
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 20, 0)
        spinbox_layout.addWidget(self.red_line_label_x)
        spinbox_layout.addWidget(self.x_red_line_spinbox)
        spinbox_layout.addWidget(self.red_line_label_y)

        btns_layout = QHBoxLayout()
        # btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        btns_layout.setContentsMargins(20, 0, 0, 0)
        btns_layout.addLayout(spinbox_layout)
        btns_layout.addWidget(self.cut_button, 0, Qt.AlignmentFlag.AlignRight)

        # Создаем виджет Matplotlib для вывода графиков
        self.canvas = FigureCanvas(Figure(figsize=(16, 16)))

        self.addLayout(btns_layout)
        self.addWidget(self.canvas)

        self.las = None

        self.gamma_graph_data: GraphData = None
        self.neutronic_graph_data: GraphData = None

        self.is_gamma = False
        self.is_neutronic = False

        self.size_entry = 0
        self.smooth_count_entry = 0
        
        self.axes = []
        self.col_num = []

        # Создание красной вертикальной линии
        self.spinbox_max_value = 2147483647
        self.red_line = []
        self.move_x = 0
        self.dragging = False

    
    def set_las(self, las: LASFile):
        self.las = las

    def set_is_gamma(self, is_gamma):
        self.is_gamma = is_gamma

    def set_is_neutronic(self, is_neutronic):
        self.is_neutronic = is_neutronic

    def define_device_type(self):
        self.set_is_gamma("RSD" in self.las.keys())
        self.set_is_neutronic("NTNC" in self.las.keys())

    def set_size_entry(self, size_entry):
        self.size_entry = size_entry

    def set_smooth_count_entry(self, smooth_count_entry):
        self.smooth_count_entry = smooth_count_entry


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

    def create_figure(self, col_num):
        fig, self.axes = plt.subplots(4, col_num, figsize=(8, 6))
        # print(self.axes)

        fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)

        self.canvas.figure = fig

    def ensure_figure_created(self):
        # if len(self.axes) == 0:
        if self.is_gamma and self.is_neutronic:
            self.col_num = 2
        else:
            self.col_num = 1

        self.create_figure(self.col_num)


    def get_data_from_las(self):
        self.gamma_graph_data = None
        self.neutronic_graph_data = None
        if self.is_gamma:
            self.gamma_graph_data = self.get_data(ColumnDataGamma)
        if self.is_neutronic:
            self.neutronic_graph_data = self.get_data(ColumnDataNeutronic)

    def get_data(self, abs_column_data: Type[AbstractColumnData]) -> GraphData:
        graph_data = GraphData()
        column_data = abs_column_data()

        graph_data.near_probe = self.las[column_data.near_probe]
        graph_data.far_probe = self.las[column_data.far_probe]
        graph_data.time = self.las["TIME"]
        if self.is_gamma and self.is_neutronic:
            graph_data.temper = self.las[column_data.temper]
        else:
            graph_data.temper = self.las[column_data.default_temper]

        if self.is_gamma and not self.is_neutronic:
            graph_data.near_probe_threshold = int(self.las[column_data.near_probe_threshold][0])
            graph_data.far_probe_threshold = int(self.las[column_data.far_probe_threshold][0])
        else:
            graph_data.near_probe_threshold = '\t\t'
            graph_data.far_probe_threshold = '\t\t'

        return graph_data


    def clear_graphs(self):
        if self.col_num == 2:
            for col_axes in self.axes:
                for ax in col_axes:
                    ax.clear()
        else:
            for ax in self.axes:
                ax.clear()

    def crop_data(self):
        if self.is_gamma:
            self.gamma_graph_data.near_probe = self.gamma_graph_data.near_probe[self.move_x:]
            self.gamma_graph_data.far_probe = self.gamma_graph_data.far_probe[self.move_x:]
            self.gamma_graph_data.far_on_near_probe = self.gamma_graph_data.far_on_near_probe[self.move_x:]
            self.gamma_graph_data.temper = self.gamma_graph_data.temper[self.move_x:]
            self.gamma_graph_data.time = self.gamma_graph_data.time[self.move_x:]
            self.spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1

        if self.is_neutronic:
            self.neutronic_graph_data.near_probe = self.neutronic_graph_data.near_probe[self.move_x:]
            self.neutronic_graph_data.far_probe = self.neutronic_graph_data.far_probe[self.move_x:]
            self.neutronic_graph_data.far_on_near_probe = self.neutronic_graph_data.far_on_near_probe[self.move_x:]
            self.neutronic_graph_data.temper = self.neutronic_graph_data.temper[self.move_x:]
            self.neutronic_graph_data.time = self.neutronic_graph_data.time[self.move_x:]
            self.spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1


    def update_red_line_label(self, line_pos_x):
        label_text = ''
        if self.is_gamma:
            NEAR_PROBE_Y = int(np.round(self.gamma_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.gamma_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.gamma_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.gamma_graph_data.temper[line_pos_x])
            label_text = f'\t{ColumnDataGamma.near_probe} Y: {NEAR_PROBE_Y}\t{ColumnDataGamma.far_probe} Y: {FAR_PROBE_Y}\t{ColumnDataGamma.far_probe}/{ColumnDataGamma.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        if self.is_neutronic:
            NEAR_PROBE_Y = int(np.round(self.neutronic_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.neutronic_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.neutronic_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.neutronic_graph_data.temper[line_pos_x])
            label_text = f'\t{ColumnDataNeutronic.near_probe} Y: {NEAR_PROBE_Y}\t{ColumnDataNeutronic.far_probe} Y: {FAR_PROBE_Y}\t{ColumnDataNeutronic.far_probe}/{ColumnDataNeutronic.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        self.red_line_label_y.setText(label_text)
        

    def ensure_red_line_created(self):
        if self.col_num == 2:
            for col_axes in self.axes:
                for ax in col_axes:
                    self.red_line.append(ax.axvline(0, color='red'))
        else:
            for ax in self.axes:
                self.red_line.append(ax.axvline(0, color='red'))


        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def draw_red_line(self):
        if self.col_num == 2:
            i = 0
            for col_axes in self.axes:
                for ax in col_axes:
                    self.red_line[i].remove()
                    self.red_line[i] = ax.axvline(self.move_x, color='red')
                    i += 1
        else:
            for i, ax in enumerate(self.axes):
                self.red_line[i].remove()
                self.red_line[i] = ax.axvline(self.move_x, color='red')

        # for i, ax in enumerate(self.axes):
        #     self.red_line[i].remove()
        #     self.red_line[i] = ax.axvline(self.move_x, color='red')
        self.canvas.draw()

    def update_red_line(self, new_value):
        if self.axes is None:
            return
        
        if self.spinbox_max_value + 1 < new_value:
            new_value = self.spinbox_max_value + 1

        if new_value < 0:
            new_value = 0
        
        self.move_x = new_value
        
        self.update_red_line_label(self.move_x)

        self.draw_red_line()


    def update_graphs(self):
        if self.is_gamma and self.is_neutronic:
            # print('self.gamma_graph_data.time', self.gamma_graph_data.time)
            # print('self.neutronic_graph_data.far_on_near_probe', self.neutronic_graph_data.far_on_near_probe)
            create_graph_on_canvas(self.axes[0, 0], self.gamma_graph_data.time, self.gamma_graph_data.near_probe, f"{ColumnDataGamma.near_probe}_1")
            create_graph_on_canvas(self.axes[1, 0], self.gamma_graph_data.time, self.gamma_graph_data.far_probe, f"{ColumnDataGamma.far_probe}_1")
            create_graph_on_canvas(self.axes[2, 0], self.gamma_graph_data.time, self.gamma_graph_data.far_on_near_probe, f"{ColumnDataGamma.far_probe}/{ColumnDataGamma.near_probe}")
            create_graph_on_canvas(self.axes[3, 0], self.gamma_graph_data.time, self.gamma_graph_data.temper, "TEMPER")
            create_graph_on_canvas(self.axes[0, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.near_probe, f"{ColumnDataNeutronic.near_probe}_1")
            create_graph_on_canvas(self.axes[1, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_probe, f"{ColumnDataNeutronic.far_probe}_1")
            create_graph_on_canvas(self.axes[2, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_on_near_probe, f"{ColumnDataNeutronic.far_probe}/{ColumnDataNeutronic.near_probe}")
            create_graph_on_canvas(self.axes[3, 1], self.gamma_graph_data.time, self.gamma_graph_data.temper, "TEMPER")
        elif self.is_gamma:
            create_graph_on_canvas(self.axes[0], self.gamma_graph_data.time, self.gamma_graph_data.near_probe, f"{ColumnDataGamma.near_probe}_1")
            create_graph_on_canvas(self.axes[1], self.gamma_graph_data.time, self.gamma_graph_data.far_probe, f"{ColumnDataGamma.far_probe}_1")
            create_graph_on_canvas(self.axes[2], self.gamma_graph_data.time, self.gamma_graph_data.far_on_near_probe, f"{ColumnDataGamma.far_probe}/{ColumnDataGamma.near_probe}")
            create_graph_on_canvas(self.axes[3], self.gamma_graph_data.time, self.gamma_graph_data.temper, "TEMPER")
        elif self.is_neutronic:
            create_graph_on_canvas(self.axes[0], self.neutronic_graph_data.time, self.neutronic_graph_data.near_probe, f"{ColumnDataNeutronic.near_probe}_1")
            create_graph_on_canvas(self.axes[1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_probe, f"{ColumnDataNeutronic.far_probe}_1")
            create_graph_on_canvas(self.axes[2], self.neutronic_graph_data.time, self.neutronic_graph_data.far_on_near_probe, f"{ColumnDataNeutronic.far_probe}/{ColumnDataNeutronic.near_probe}")
            create_graph_on_canvas(self.axes[3], self.neutronic_graph_data.time, self.neutronic_graph_data.temper, "TEMPER")


    def plot_graphs(self):
        if self.las is None:
            return
        
        self.ensure_figure_created()
        self.ensure_red_line_created()
        
        self.clear_graphs()
        
        self.get_data_from_las()
        self.calc_data()

        self.update_graphs()

        self.x_red_line_spinbox.setMaximum(self.spinbox_max_value)
        self.x_red_line_spinbox.setValue(0)
        if self.move_x == 0:
            self.draw_red_line()

        self.canvas.draw()

    def crop_graphs(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data()

        self.update_graphs()

        self.x_red_line_spinbox.setMaximum(self.spinbox_max_value)
        self.x_red_line_spinbox.setValue(0)
        if self.move_x == 0:
            self.draw_red_line()

        self.canvas.draw()

    def smooth_graph(self, graph_data: GraphData) -> GraphData:
        graph_data.near_probe = smoothing_function(
            graph_data.near_probe, 
            int(self.size_entry), 
            int(self.smooth_count_entry)
        )
        graph_data.far_probe = smoothing_function(
            graph_data.far_probe, 
            int(self.size_entry), 
            int(self.smooth_count_entry)
        )
        graph_data.far_on_near_probe = np.divide(graph_data.far_probe, graph_data.near_probe)
        delta_len = len(graph_data.time) - len(graph_data.near_probe)
        # padded_graph_data.near_probe = np.pad(graph_data.near_probe, (delta_len, 0), mode='constant')
        graph_data.time = graph_data.time[delta_len:]
        graph_data.temper = graph_data.temper[delta_len:]

        return graph_data

    def calc_data(self):
        if self.is_gamma:
            self.gamma_graph_data = self.smooth_graph(self.gamma_graph_data)
            self.spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1
        
        if self.is_neutronic:
            self.neutronic_graph_data = self.smooth_graph(self.neutronic_graph_data)
            self.spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1