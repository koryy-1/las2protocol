from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsScene
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from lasio import LASFile
from typing import Type

from models.ColumnData import AbstractColumnData, ColumnDataGamma, ColumnDataNeutronic
from models.GraphData import GraphData
from utils import smoothing_function
from graph_layout.ToolBox import ToolBox
from calculations import initialize_base_values, calculate_extremum_values_with_indexes
from models.TempType import TempType

class GraphCanvas(QWidget):
    def __init__(self, column_data: AbstractColumnData):
        super().__init__()

        self.column_data = column_data

        # panels for control vert lines
        self.tool_box = ToolBox(
            self.crop_graphs,
            self.update_left_line,
            self.update_right_line
        )

        # Создаем виджет Matplotlib для вывода графиков
        self.figure = Figure(figsize=(16, 16))
        self.canvas = FigureCanvas(self.figure)
        # self.scene = QGraphicsScene()
        # self.view = self.scene.addWidget(self.canvas)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addLayout(self.tool_box)
        self.setLayout(layout)

        self.las = None

        self.graph_data: GraphData = None
        self.neutronic_graph_data: GraphData = None

        self.size_entry = 0
        self.smooth_count_entry = 0
        
        self.axes: np.flatiter[np.ndarray] = []

        # Создание красной вертикальной линии
        self.left_line = []
        self.right_line = []
        self.left_vline_x = 0
        self.right_vline_x = 0
        self.left_dragging = False
        self.right_dragging = False

        self.is_clear_graphs = True

    
    def set_las(self, las: LASFile):
        self.las = las

    def set_size_entry(self, size_entry):
        self.size_entry = size_entry

    def set_smooth_count_entry(self, smooth_count_entry):
        self.smooth_count_entry = smooth_count_entry

    def set_is_clear_graphs(self, value: bool):
        self.is_clear_graphs = value

    def on_mouse_press(self, event):
        if event.button == 1 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.left_dragging = True

            self.left_vline_x = int(event.xdata)
            self.tool_box.left_line_spinbox_x.setValue(self.left_vline_x)

        if event.button == 3 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.right_dragging = True

            self.right_vline_x = int(event.xdata)
            self.tool_box.right_line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_move(self, event):
        if self.left_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.left_vline_x = int(event.xdata)
            self.tool_box.left_line_spinbox_x.setValue(self.left_vline_x)

        if self.right_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.right_vline_x = int(event.xdata)
            self.tool_box.right_line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_release(self, event):
        if self.left_dragging:
            self.left_dragging = False
            # print("release", int(event.xdata))

        if self.right_dragging:
            self.right_dragging = False
            # print("release", int(event.xdata))
        
    def create_figure(self):
        print('create ', self.column_data.near_probe)
        self.figure = Figure(figsize=(7, 9))
        self.figure.subplots_adjust(hspace=0.4)

        for i in range(4):
            self.axes.append(self.figure.add_subplot(4, 1, i + 1))

        self.figure.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.figure.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        
        self.canvas.figure = self.figure
        self.canvas.draw()

    def ensure_figure_created(self):
        if len(self.axes) == 0:
            self.create_figure()

    def clear(self):
        if len(self.axes) != 0:
            print('clear', self.column_data.near_probe)
            self.figure.clear()
            self.figure = None
            self.axes.clear()
            self.canvas.draw()

    def clear_graphs(self):
        for ax in self.axes:
            ax.clear()


    def get_data_from_las(self):
        self.graph_data = self.get_data()

    def get_data(self) -> GraphData:
        graph_data = GraphData()

        graph_data.near_probe = self.las[self.column_data.near_probe]
        graph_data.far_probe = self.las[self.column_data.far_probe]
        graph_data.time = self.las["TIME"]

        if self.column_data.temper in self.las.keys():
            graph_data.temper = self.las[self.column_data.temper]
        elif self.column_data.default_temper in self.las.keys():
            graph_data.temper = self.las[self.column_data.default_temper]
        else:
            graph_data.temper = np.zeros(len(graph_data.time))

        graph_data.near_probe_threshold = '\t\t'
        graph_data.far_probe_threshold = '\t\t'

        if self.column_data.near_probe_threshold in self.las.keys():
            graph_data.near_probe_threshold = int(self.las[self.column_data.near_probe_threshold][0])
        if self.column_data.far_probe_threshold in self.las.keys():
            graph_data.far_probe_threshold = int(self.las[self.column_data.far_probe_threshold][0])

        return graph_data


    def crop_data(self):
        self.graph_data.near_probe = self.graph_data.near_probe[self.left_vline_x:self.right_vline_x + 1]
        self.graph_data.far_probe = self.graph_data.far_probe[self.left_vline_x:self.right_vline_x + 1]
        self.graph_data.far_on_near_probe = self.graph_data.far_on_near_probe[self.left_vline_x:self.right_vline_x + 1]
        self.graph_data.temper = self.graph_data.temper[self.left_vline_x:self.right_vline_x + 1]
        self.graph_data.time = self.graph_data.time[self.left_vline_x:self.right_vline_x + 1]
        if len(self.graph_data.near_probe) - 1 > self.right_spinbox_max_value:
            self.left_spinbox_max_value = self.right_spinbox_max_value
        else:
            self.left_spinbox_max_value = len(self.graph_data.near_probe) - 1
        self.right_spinbox_max_value = len(self.graph_data.near_probe) - 1


    def ensure_left_line_created(self):
        for ax in self.axes:
            self.left_line.append(ax.axvline(0, color='red'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def ensure_right_line_created(self):
        for ax in self.axes:
            self.right_line.append(ax.axvline(0, color='blue'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def draw_left_line(self):
        for i, ax in enumerate(self.axes):
            self.left_line[i].remove()
            self.left_line[i] = ax.axvline(self.left_vline_x, color='red')

        self.canvas.draw()

    def draw_right_line(self):
        for i, ax in enumerate(self.axes):
            self.right_line[i].remove()
            self.right_line[i] = ax.axvline(self.right_vline_x, color='blue')

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
        
        # self.update_left_line_label(self.left_vline_x)

        self.draw_left_line()

    def update_right_line(self, new_value):
        if self.axes is None:
            return
        
        if self.right_spinbox_max_value + 1 < new_value:
            new_value = self.right_spinbox_max_value + 1

        if new_value < 0:
            new_value = 0
        
        self.right_vline_x = new_value
        
        # self.update_right_line_label(self.right_vline_x)

        self.draw_right_line()


    def update_graphs(self):
        self.create_graph_on_canvas(self.axes[0], self.graph_data.time, self.graph_data.near_probe, f"{self.column_data.near_probe}_1")
        self.create_graph_on_canvas(self.axes[1], self.graph_data.time, self.graph_data.far_probe, f"{self.column_data.far_probe}_1")
        self.create_graph_on_canvas(self.axes[2], self.graph_data.time, self.graph_data.far_on_near_probe, f"{self.column_data.far_probe}/{self.column_data.near_probe}")
        self.create_graph_on_canvas(self.axes[3], self.graph_data.time, self.graph_data.temper, "TEMPER")

    def create_graph_on_canvas(self, ax: Axes, x, y, plot_title: str):
        # print(plot_title, y)
        ax.plot(y, label=plot_title, linewidth=2)

        self.figure.tight_layout()

        fontsize = 12
        # plt.rc('font', size=fontsize) #controls default text size
        # plt.rc('axes', titlesize=fontsize) #fontsize of the title
        # plt.rc('axes', labelsize=fontsize) #fontsize of the x and y labels
        # plt.rc('legend', fontsize=fontsize) #fontsize of the legend

        ax.xaxis.set_tick_params(labelsize=fontsize, width=1)
        ax.yaxis.set_tick_params(labelsize=fontsize, width=1)

        ax.xaxis.grid(True, linewidth=1, alpha=1, color='black')
        ax.yaxis.grid(True, linewidth=1, alpha=1, color='black')

        ax.legend(loc='right', fontsize=fontsize)
        
        try:
            ax.set_ylim(y[np.isfinite(y)].min() * 0.9, y[np.isfinite(y)].max() * 1.1)
        except:
            print(f"no {plot_title}")
        ax.set_xlim(-(len(x) * 0.02), len(x) * 1.23)


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
        self.graph_data = self.smooth_graph(self.graph_data)
        self.left_spinbox_max_value = len(self.graph_data.near_probe) - 1
        self.right_spinbox_max_value = len(self.graph_data.near_probe) - 1
        
    def plot_graphs(self):
        if self.las is None:
            return
        
        self.ensure_figure_created()
        self.ensure_left_line_created()
        self.ensure_right_line_created()
        
        if self.is_clear_graphs:
            self.clear_graphs()
        
        self.get_data_from_las()
        self.calc_data()

        self.update_graphs()
        
        self.tool_box.left_line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.tool_box.left_line_spinbox_x.setValue(0)
        if self.left_vline_x == 0:
            self.draw_left_line()

        self.tool_box.right_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.tool_box.right_line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def crop_graphs(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data()

        self.update_graphs()

        self.tool_box.left_line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.tool_box.left_line_spinbox_x.setValue(0)
        if self.left_vline_x == 0 or self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()
            
        self.tool_box.right_line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.tool_box.right_line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def mark_extreme_points(self, is_heat, is_cool):
        # calcs
        near_probe_heat_x = []
        near_probe_heat_y = []

        far_probe_heat_x = []
        far_probe_heat_y = []

        far_on_near_probe_heat_x = []
        far_on_near_probe_heat_y = []

        near_probe_cool_x = []
        near_probe_cool_y = []

        far_probe_cool_x = []
        far_probe_cool_y = []

        far_on_near_probe_cool_x = []
        far_on_near_probe_cool_y = []
        if is_heat:
            near_probe_base, far_probe_base, far_on_near_probe_base, T_base = initialize_base_values(
                TempType.HEATING, int(self.size_entry), self.graph_data.temper, self.graph_data.near_probe, self.graph_data.far_probe, self.graph_data.far_on_near_probe
            )

            (near_probe_max, far_probe_max, far_on_near_probe_max, 
            near_probe_min, far_probe_min, far_on_near_probe_min) = calculate_extremum_values_with_indexes(
                self.graph_data.near_probe, self.graph_data.far_probe, self.graph_data.far_on_near_probe, near_probe_base, 
                far_probe_base, far_on_near_probe_base, self.graph_data.temper, T_base, TempType.HEATING
            )

            near_probe_heat_x = [0, near_probe_max[0], near_probe_min[0]]
            near_probe_heat_y = [near_probe_base, near_probe_max[1], near_probe_min[1]]

            far_probe_heat_x = [0, far_probe_max[0], far_probe_min[0]]
            far_probe_heat_y = [far_probe_base, far_probe_max[1], far_probe_min[1]]

            far_on_near_probe_heat_x = [0, far_on_near_probe_max[0], far_on_near_probe_min[0]]
            far_on_near_probe_heat_y = [far_on_near_probe_base, far_on_near_probe_max[1], far_on_near_probe_min[1]]

        if is_cool:
            near_probe_base, far_probe_base, far_on_near_probe_base, T_base = initialize_base_values(
                TempType.COOLING, int(self.size_entry), self.graph_data.temper, self.graph_data.near_probe, self.graph_data.far_probe, self.graph_data.far_on_near_probe
            )

            (near_probe_max, far_probe_max, far_on_near_probe_max, 
            near_probe_min, far_probe_min, far_on_near_probe_min) = calculate_extremum_values_with_indexes(
                self.graph_data.near_probe, self.graph_data.far_probe, self.graph_data.far_on_near_probe, near_probe_base, 
                far_probe_base, far_on_near_probe_base, self.graph_data.temper, T_base, TempType.COOLING
            )

            near_probe_cool_x = [len(self.graph_data.temper), near_probe_max[0], near_probe_min[0]]
            near_probe_cool_y = [near_probe_base, near_probe_max[1], near_probe_min[1]]

            far_probe_cool_x = [len(self.graph_data.temper), far_probe_max[0], far_probe_min[0]]
            far_probe_cool_y = [far_probe_base, far_probe_max[1], far_probe_min[1]]

            far_on_near_probe_cool_x = [len(self.graph_data.temper), far_on_near_probe_max[0], far_on_near_probe_min[0]]
            far_on_near_probe_cool_y = [far_on_near_probe_base, far_on_near_probe_max[1], far_on_near_probe_min[1]]

        near_probe_heat_x.extend(near_probe_cool_x)
        near_probe_heat_y.extend(near_probe_cool_y)

        far_probe_heat_x.extend(far_probe_cool_x)
        far_probe_heat_y.extend(far_probe_cool_y)

        far_on_near_probe_heat_x.extend(far_on_near_probe_cool_x)
        far_on_near_probe_heat_y.extend(far_on_near_probe_cool_y)

        self.axes[0].scatter(near_probe_heat_x, near_probe_heat_y, color='red', label='Extremum')
        self.axes[1].scatter(far_probe_heat_x, far_probe_heat_y, color='red', label='Extremum')
        self.axes[2].scatter(far_on_near_probe_heat_x, far_on_near_probe_heat_y, color='red', label='Extremum')

        self.canvas.draw()
