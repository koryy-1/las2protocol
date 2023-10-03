from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QGraphicsScene
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

        self.column_data_gamma = ColumnDataGamma()
        self.column_data_neutronic = ColumnDataNeutronic()

        ################################# left
        # Создание кнопки "Обрезать"
        self.cut_button = QPushButton("Обрезать")
        self.cut_button.clicked.connect(self.crop_graphs_on_left)

        # красная линия
        self.red_line_label_x = QLabel("Левая линия X: ")
        self.left_line_label_y = QLabel("")
        self.left_line_spinbox_x = QSpinBox()
        self.left_line_spinbox_x.setMaximum(2147483647)
        self.left_line_spinbox_x.valueChanged.connect(self.update_left_line)

        # layout for spinbox
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 20, 0)
        spinbox_layout.addWidget(self.red_line_label_x)
        spinbox_layout.addWidget(self.left_line_spinbox_x)
        spinbox_layout.addWidget(self.left_line_label_y)

        left_btns_layout = QHBoxLayout()
        # btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_btns_layout.setContentsMargins(20, 0, 0, 0)
        left_btns_layout.addLayout(spinbox_layout)
        left_btns_layout.addWidget(self.cut_button, 0, Qt.AlignmentFlag.AlignRight)

        ############################## right
        # Создание кнопки "Обрезать"
        self.right_cut_button = QPushButton("Обрезать")
        self.right_cut_button.clicked.connect(self.crop_graphs_on_right)

        # красная линия
        self.right_line_label_x = QLabel("Правая линия line X: ")
        self.right_line_label_y = QLabel("")
        self.right_line_spinbox_x = QSpinBox()
        self.right_line_spinbox_x.setMaximum(2147483647)
        self.right_line_spinbox_x.valueChanged.connect(self.update_right_line)

        # layout for spinbox
        right_spinbox_layout = QHBoxLayout()
        right_spinbox_layout.setContentsMargins(0, 0, 20, 0)
        right_spinbox_layout.addWidget(self.right_line_label_x)
        right_spinbox_layout.addWidget(self.right_line_spinbox_x)
        right_spinbox_layout.addWidget(self.right_line_label_y)

        right_btns_layout = QHBoxLayout()
        # btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        right_btns_layout.setContentsMargins(20, 0, 0, 0)
        right_btns_layout.addLayout(right_spinbox_layout)
        right_btns_layout.addWidget(self.right_cut_button, 0, Qt.AlignmentFlag.AlignRight)

        # Создаем виджет Matplotlib для вывода графиков
        self.canvas = FigureCanvas(Figure(figsize=(16, 16)))
        # self.scene = QGraphicsScene()
        # self.view = self.scene.addWidget(self.canvas)

        self.addWidget(self.canvas)
        self.addLayout(left_btns_layout)
        self.addLayout(right_btns_layout)

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
        self.left_spinbox_max_value = 2147483647
        self.right_spinbox_max_value = 2147483647
        self.left_line = []
        self.right_line = []
        self.left_vline_x = 0
        self.right_vline_x = 0
        self.left_dragging = False
        self.right_dragging = False

    
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
            self.left_dragging = True

            self.left_vline_x = int(event.xdata)
            self.left_line_spinbox_x.setValue(self.left_vline_x)

        if event.button == 3 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.right_dragging = True

            self.right_vline_x = int(event.xdata)
            self.right_line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_move(self, event):
        if self.left_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.left_vline_x = int(event.xdata)
            self.left_line_spinbox_x.setValue(self.left_vline_x)

        if self.right_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.right_vline_x = int(event.xdata)
            self.right_line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_release(self, event):
        if self.left_dragging:
            self.left_dragging = False
            # print("release", int(event.xdata))

        if self.right_dragging:
            self.right_dragging = False
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
            self.gamma_graph_data = self.get_data(self.column_data_gamma)
        if self.is_neutronic:
            self.neutronic_graph_data = self.get_data(self.column_data_neutronic)

    def get_data(self, abs_column_data: AbstractColumnData) -> GraphData:
        graph_data = GraphData()

        graph_data.near_probe = self.las[abs_column_data.near_probe]
        graph_data.far_probe = self.las[abs_column_data.far_probe]
        graph_data.time = self.las["TIME"]
        if self.is_gamma and self.is_neutronic:
            graph_data.temper = self.las[abs_column_data.temper]
        else:
            graph_data.temper = self.las[abs_column_data.default_temper]

        if self.is_gamma and not self.is_neutronic:
            graph_data.near_probe_threshold = int(self.las[abs_column_data.near_probe_threshold][0])
            graph_data.far_probe_threshold = int(self.las[abs_column_data.far_probe_threshold][0])
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

    def crop_data_on_left(self):
        if self.is_gamma:
            self.gamma_graph_data.near_probe = self.gamma_graph_data.near_probe[self.left_vline_x:]
            self.gamma_graph_data.far_probe = self.gamma_graph_data.far_probe[self.left_vline_x:]
            self.gamma_graph_data.far_on_near_probe = self.gamma_graph_data.far_on_near_probe[self.left_vline_x:]
            self.gamma_graph_data.temper = self.gamma_graph_data.temper[self.left_vline_x:]
            self.gamma_graph_data.time = self.gamma_graph_data.time[self.left_vline_x:]
            if len(self.gamma_graph_data.near_probe) - 1 > self.right_spinbox_max_value:
                self.left_spinbox_max_value = self.right_spinbox_max_value
            else:
                self.left_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1
            self.right_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1


        if self.is_neutronic:
            self.neutronic_graph_data.near_probe = self.neutronic_graph_data.near_probe[self.left_vline_x:]
            self.neutronic_graph_data.far_probe = self.neutronic_graph_data.far_probe[self.left_vline_x:]
            self.neutronic_graph_data.far_on_near_probe = self.neutronic_graph_data.far_on_near_probe[self.left_vline_x:]
            self.neutronic_graph_data.temper = self.neutronic_graph_data.temper[self.left_vline_x:]
            self.neutronic_graph_data.time = self.neutronic_graph_data.time[self.left_vline_x:]
            if len(self.neutronic_graph_data.near_probe) - 1 > self.right_spinbox_max_value:
                self.left_spinbox_max_value = self.right_spinbox_max_value
            else:
                self.left_spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1
            self.right_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1

    def crop_data_on_right(self):
        if self.is_gamma:
            self.gamma_graph_data.near_probe = self.gamma_graph_data.near_probe[:self.right_vline_x + 1]
            self.gamma_graph_data.far_probe = self.gamma_graph_data.far_probe[:self.right_vline_x + 1]
            self.gamma_graph_data.far_on_near_probe = self.gamma_graph_data.far_on_near_probe[:self.right_vline_x + 1]
            self.gamma_graph_data.temper = self.gamma_graph_data.temper[:self.right_vline_x + 1]
            self.gamma_graph_data.time = self.gamma_graph_data.time[:self.right_vline_x + 1]
            self.right_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1

        if self.is_neutronic:
            self.neutronic_graph_data.near_probe = self.neutronic_graph_data.near_probe[:self.right_vline_x + 1]
            self.neutronic_graph_data.far_probe = self.neutronic_graph_data.far_probe[:self.right_vline_x + 1]
            self.neutronic_graph_data.far_on_near_probe = self.neutronic_graph_data.far_on_near_probe[:self.right_vline_x + 1]
            self.neutronic_graph_data.temper = self.neutronic_graph_data.temper[:self.right_vline_x + 1]
            self.neutronic_graph_data.time = self.neutronic_graph_data.time[:self.right_vline_x + 1]
            self.right_spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1


    def update_left_line_label(self, line_pos_x):
        label_text = ''
        if self.is_gamma:
            NEAR_PROBE_Y = int(np.round(self.gamma_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.gamma_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.gamma_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.gamma_graph_data.temper[line_pos_x])
            label_text = f'\t{self.column_data_gamma.near_probe} Y: {NEAR_PROBE_Y}\t{self.column_data_gamma.far_probe} Y: {FAR_PROBE_Y}\t{self.column_data_gamma.far_probe}/{self.column_data_gamma.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        if self.is_neutronic:
            NEAR_PROBE_Y = int(np.round(self.neutronic_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.neutronic_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.neutronic_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.neutronic_graph_data.temper[line_pos_x])
            label_text = label_text + f'\t{self.column_data_neutronic.near_probe} Y: {NEAR_PROBE_Y}\t{self.column_data_neutronic.far_probe} Y: {FAR_PROBE_Y}\t{self.column_data_neutronic.far_probe}/{self.column_data_neutronic.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        self.left_line_label_y.setText(label_text)

    def update_right_line_label(self, line_pos_x):
        label_text = ''
        if self.is_gamma:
            NEAR_PROBE_Y = int(np.round(self.gamma_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.gamma_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.gamma_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.gamma_graph_data.temper[line_pos_x])
            label_text = f'\t{self.column_data_gamma.near_probe} Y: {NEAR_PROBE_Y}\t{self.column_data_gamma.far_probe} Y: {FAR_PROBE_Y}\t{self.column_data_gamma.far_probe}/{self.column_data_gamma.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        if self.is_neutronic:
            NEAR_PROBE_Y = int(np.round(self.neutronic_graph_data.near_probe[line_pos_x]))
            FAR_PROBE_Y = int(np.round(self.neutronic_graph_data.far_probe[line_pos_x]))
            FAR_ON_NEAR_PROBE_Y = np.round(self.neutronic_graph_data.far_on_near_probe[line_pos_x], 3)
            TEMPER_Y = int(self.neutronic_graph_data.temper[line_pos_x])
            label_text = label_text + f'\t{self.column_data_neutronic.near_probe} Y: {NEAR_PROBE_Y}\t{self.column_data_neutronic.far_probe} Y: {FAR_PROBE_Y}\t{self.column_data_neutronic.far_probe}/{self.column_data_neutronic.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
        self.right_line_label_y.setText(label_text)
        

    def ensure_left_line_created(self):
        if self.col_num == 2:
            for col_axes in self.axes:
                for ax in col_axes:
                    self.left_line.append(ax.axvline(0, color='red'))
        else:
            for ax in self.axes:
                self.left_line.append(ax.axvline(0, color='red'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def ensure_right_line_created(self):
        if self.col_num == 2:
            for col_axes in self.axes:
                for ax in col_axes:
                    self.right_line.append(ax.axvline(0, color='blue'))
        else:
            for ax in self.axes:
                self.right_line.append(ax.axvline(0, color='blue'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def draw_left_line(self):
        if self.col_num == 2:
            i = 0
            for col_axes in self.axes:
                for ax in col_axes:
                    self.left_line[i].remove()
                    self.left_line[i] = ax.axvline(self.left_vline_x, color='red')
                    i += 1
        else:
            for i, ax in enumerate(self.axes):
                self.left_line[i].remove()
                self.left_line[i] = ax.axvline(self.left_vline_x, color='red')

        # for i, ax in enumerate(self.axes):
        #     self.red_line[i].remove()
        #     self.red_line[i] = ax.axvline(self.move_x, color='red')
        self.canvas.draw()

    def draw_right_line(self):
        if self.col_num == 2:
            i = 0
            for col_axes in self.axes:
                for ax in col_axes:
                    self.right_line[i].remove()
                    self.right_line[i] = ax.axvline(self.right_vline_x, color='blue')
                    i += 1
        else:
            for i, ax in enumerate(self.axes):
                self.right_line[i].remove()
                self.right_line[i] = ax.axvline(self.right_vline_x, color='blue')

        # for i, ax in enumerate(self.axes):
        #     self.red_line[i].remove()
        #     self.red_line[i] = ax.axvline(self.move_x, color='red')
        self.canvas.draw()

    def update_left_line(self, new_value):
        if self.axes is None:
            return
        
        # todo: limits for left and right spinbox
        if self.left_spinbox_max_value + 1 < new_value:
            new_value = self.left_spinbox_max_value + 1

        if new_value < 0:
            new_value = 0
        
        self.left_vline_x = new_value
        
        self.update_left_line_label(self.left_vline_x)

        self.draw_left_line()

    def update_right_line(self, new_value):
        if self.axes is None:
            return
        
        if self.right_spinbox_max_value + 1 < new_value:
            new_value = self.right_spinbox_max_value + 1

        if new_value < 0:
            new_value = 0
        
        self.right_vline_x = new_value
        
        self.update_right_line_label(self.right_vline_x)

        self.draw_right_line()


    def update_graphs(self):
        if self.is_gamma and self.is_neutronic:
            # print('self.gamma_graph_data.time', self.gamma_graph_data.time)
            # print('self.neutronic_graph_data.far_on_near_probe', self.neutronic_graph_data.far_on_near_probe)
            create_graph_on_canvas(self.axes[0, 0], self.gamma_graph_data.time, self.gamma_graph_data.near_probe, f"{self.column_data_gamma.near_probe}_1")
            create_graph_on_canvas(self.axes[1, 0], self.gamma_graph_data.time, self.gamma_graph_data.far_probe, f"{self.column_data_gamma.far_probe}_1")
            create_graph_on_canvas(self.axes[2, 0], self.gamma_graph_data.time, self.gamma_graph_data.far_on_near_probe, f"{self.column_data_gamma.far_probe}/{self.column_data_gamma.near_probe}")
            create_graph_on_canvas(self.axes[3, 0], self.gamma_graph_data.time, self.gamma_graph_data.temper, "TEMPER")
            create_graph_on_canvas(self.axes[0, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.near_probe, f"{self.column_data_neutronic.near_probe}_1")
            create_graph_on_canvas(self.axes[1, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_probe, f"{self.column_data_neutronic.far_probe}_1")
            create_graph_on_canvas(self.axes[2, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_on_near_probe, f"{self.column_data_neutronic.far_probe}/{self.column_data_neutronic.near_probe}")
            create_graph_on_canvas(self.axes[3, 1], self.neutronic_graph_data.time, self.neutronic_graph_data.temper, "TEMPER")
        elif self.is_gamma:
            create_graph_on_canvas(self.axes[0], self.gamma_graph_data.time, self.gamma_graph_data.near_probe, f"{self.column_data_gamma.near_probe}_1")
            create_graph_on_canvas(self.axes[1], self.gamma_graph_data.time, self.gamma_graph_data.far_probe, f"{self.column_data_gamma.far_probe}_1")
            create_graph_on_canvas(self.axes[2], self.gamma_graph_data.time, self.gamma_graph_data.far_on_near_probe, f"{self.column_data_gamma.far_probe}/{self.column_data_gamma.near_probe}")
            create_graph_on_canvas(self.axes[3], self.gamma_graph_data.time, self.gamma_graph_data.temper, "TEMPER")
        elif self.is_neutronic:
            create_graph_on_canvas(self.axes[0], self.neutronic_graph_data.time, self.neutronic_graph_data.near_probe, f"{self.column_data_neutronic.near_probe}_1")
            create_graph_on_canvas(self.axes[1], self.neutronic_graph_data.time, self.neutronic_graph_data.far_probe, f"{self.column_data_neutronic.far_probe}_1")
            create_graph_on_canvas(self.axes[2], self.neutronic_graph_data.time, self.neutronic_graph_data.far_on_near_probe, f"{self.column_data_neutronic.far_probe}/{self.column_data_neutronic.near_probe}")
            create_graph_on_canvas(self.axes[3], self.neutronic_graph_data.time, self.neutronic_graph_data.temper, "TEMPER")


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
        graph_data.far_on_near_probe = np.divide(graph_data.far_probe[np.isfinite(graph_data.far_probe)], graph_data.near_probe[np.isfinite(graph_data.near_probe)])
        delta_len = len(graph_data.time) - len(graph_data.near_probe)
        # padded_graph_data.near_probe = np.pad(graph_data.near_probe, (delta_len, 0), mode='constant')
        graph_data.time = graph_data.time[delta_len:]
        graph_data.temper = graph_data.temper[delta_len:]

        return graph_data

    def calc_data(self):
        if self.is_gamma:
            self.gamma_graph_data = self.smooth_graph(self.gamma_graph_data)
            self.left_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1
            self.right_spinbox_max_value = len(self.gamma_graph_data.near_probe) - 1
        
        if self.is_neutronic:
            self.neutronic_graph_data = self.smooth_graph(self.neutronic_graph_data)
            self.left_spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1
            self.right_spinbox_max_value = len(self.neutronic_graph_data.near_probe) - 1

    def plot_graphs(self):
        if self.las is None:
            return
        
        self.ensure_figure_created()
        self.ensure_left_line_created()
        self.ensure_right_line_created()
        
        self.clear_graphs()
        
        self.get_data_from_las()
        self.calc_data()

        self.update_graphs()
        
        self.left_line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.left_line_spinbox_x.setValue(0)
        if self.left_vline_x == 0:
            self.draw_left_line()

        self.right_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def crop_graphs_on_left(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data_on_left()

        self.update_graphs()

        self.left_line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.left_line_spinbox_x.setValue(0)
        if self.left_vline_x == 0 or self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()
            
        self.right_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def crop_graphs_on_right(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data_on_right()

        self.update_graphs()

        self.left_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.left_line_spinbox_x.setValue(0)
        if self.left_vline_x == 0:
            self.draw_right_line()

        self.right_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()