from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsScene
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
from graph_layout.ToolBox import ToolBox

class GraphCanvas(QVBoxLayout):
    def __init__(self, column_data: AbstractColumnData):
        super().__init__()

        self.column_data = column_data

        # panels for control vert lines
        self.left_tool_box = ToolBox("Левая", self.crop_graphs_on_left, self.update_left_line)

        self.right_tool_box = ToolBox("Правая", self.crop_graphs_on_right, self.update_right_line)

        # Создаем виджет Matplotlib для вывода графиков
        # self.canvas = FigureCanvas(Figure(figsize=(8, 16)))
        self.canvas = FigureCanvas(Figure(figsize=(8, 16)))
        # self.scene = QGraphicsScene()
        # self.view = self.scene.addWidget(self.canvas)

        self.addWidget(self.canvas)
        self.addLayout(self.left_tool_box)
        self.addLayout(self.right_tool_box)

        self.las = None

        self.graph_data: GraphData = None
        self.neutronic_graph_data: GraphData = None

        self.size_entry = 0
        self.smooth_count_entry = 0
        
        self.axes = []

        # Создание красной вертикальной линии
        self.left_line = []
        self.right_line = []
        self.left_vline_x = 0
        self.right_vline_x = 0
        self.left_dragging = False
        self.right_dragging = False

    
    def set_las(self, las: LASFile):
        self.las = las

    def set_size_entry(self, size_entry):
        self.size_entry = size_entry

    def set_smooth_count_entry(self, smooth_count_entry):
        self.smooth_count_entry = smooth_count_entry


    def on_mouse_press(self, event):
        if event.button == 1 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.left_dragging = True

            self.left_vline_x = int(event.xdata)
            self.left_tool_box.line_spinbox_x.setValue(self.left_vline_x)

        if event.button == 3 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.right_dragging = True

            self.right_vline_x = int(event.xdata)
            self.right_tool_box.line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_move(self, event):
        if self.left_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.left_vline_x = int(event.xdata)
            self.left_tool_box.line_spinbox_x.setValue(self.left_vline_x)

        if self.right_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.right_vline_x = int(event.xdata)
            self.right_tool_box.line_spinbox_x.setValue(self.right_vline_x)

    def on_mouse_release(self, event):
        if self.left_dragging:
            self.left_dragging = False
            # print("release", int(event.xdata))

        if self.right_dragging:
            self.right_dragging = False
            # print("release", int(event.xdata))
        
    def create_figure(self):
        fig, self.axes = plt.subplots(4, figsize=(4, 8))
        fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.canvas.figure = fig
        self.canvas.draw()

    def ensure_figure_created(self):
        # if len(self.axes) == 0:

        self.create_figure()

    def clear(self):
        if self.axes is not None:
            fig = plt.figure(figsize=(4, 8))
            self.canvas.figure = fig
            self.graph_data = None
            self.clear_graphs()

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
        # if self.is_gamma and self.is_neutronic:
        #     graph_data.temper = self.las[self.column_data.temper]
        # else:
        #     graph_data.temper = self.las[self.column_data.default_temper]

        if self.column_data.temper in self.las.keys():
            graph_data.temper = self.las[self.column_data.temper]
        else:
            graph_data.temper = self.las[self.column_data.default_temper]

        # if self.is_gamma and not self.is_neutronic:
        #     graph_data.near_probe_threshold = int(self.las[self.column_data.near_probe_threshold][0])
        #     graph_data.far_probe_threshold = int(self.las[self.column_data.far_probe_threshold][0])
        # else:
        #     graph_data.near_probe_threshold = '\t\t'
        #     graph_data.far_probe_threshold = '\t\t'

        graph_data.near_probe_threshold = '\t\t'
        graph_data.far_probe_threshold = '\t\t'

        return graph_data


    def crop_data_on_left(self):
        self.graph_data.near_probe = self.graph_data.near_probe[self.left_vline_x:]
        self.graph_data.far_probe = self.graph_data.far_probe[self.left_vline_x:]
        self.graph_data.far_on_near_probe = self.graph_data.far_on_near_probe[self.left_vline_x:]
        self.graph_data.temper = self.graph_data.temper[self.left_vline_x:]
        self.graph_data.time = self.graph_data.time[self.left_vline_x:]
        if len(self.graph_data.near_probe) - 1 > self.right_spinbox_max_value:
            self.left_spinbox_max_value = self.right_spinbox_max_value
        else:
            self.left_spinbox_max_value = len(self.graph_data.near_probe) - 1
        self.right_spinbox_max_value = len(self.graph_data.near_probe) - 1

    def crop_data_on_right(self):
        self.graph_data.near_probe = self.graph_data.near_probe[:self.right_vline_x + 1]
        self.graph_data.far_probe = self.graph_data.far_probe[:self.right_vline_x + 1]
        self.graph_data.far_on_near_probe = self.graph_data.far_on_near_probe[:self.right_vline_x + 1]
        self.graph_data.temper = self.graph_data.temper[:self.right_vline_x + 1]
        self.graph_data.time = self.graph_data.time[:self.right_vline_x + 1]
        self.right_spinbox_max_value = len(self.graph_data.near_probe) - 1


    def ensure_left_line_created(self):
        for ax in self.axes.flat:
            self.left_line.append(ax.axvline(0, color='red'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def ensure_right_line_created(self):
        for ax in self.axes.flat:
            self.right_line.append(ax.axvline(0, color='blue'))

        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def draw_left_line(self):
        for i, ax in enumerate(self.axes.flat):
            self.left_line[i].remove()
            self.left_line[i] = ax.axvline(self.left_vline_x, color='red')

        self.canvas.draw()

    def draw_right_line(self):
        for i, ax in enumerate(self.axes.flat):
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
        create_graph_on_canvas(self.axes[0], self.graph_data.time, self.graph_data.near_probe, f"{self.column_data.near_probe}_1")
        create_graph_on_canvas(self.axes[1], self.graph_data.time, self.graph_data.far_probe, f"{self.column_data.far_probe}_1")
        create_graph_on_canvas(self.axes[2], self.graph_data.time, self.graph_data.far_on_near_probe, f"{self.column_data.far_probe}/{self.column_data.near_probe}")
        create_graph_on_canvas(self.axes[3], self.graph_data.time, self.graph_data.temper, "TEMPER")


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
        
        self.clear_graphs()
        
        self.get_data_from_las()
        self.calc_data()

        self.update_graphs()
        
        self.left_tool_box.line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.left_tool_box.line_spinbox_x.setValue(0)
        if self.left_vline_x == 0:
            self.draw_left_line()

        self.right_tool_box.line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_tool_box.line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def crop_graphs_on_left(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data_on_left()

        self.update_graphs()

        self.left_tool_box.line_spinbox_x.setMaximum(self.left_spinbox_max_value)
        self.left_tool_box.line_spinbox_x.setValue(0)
        if self.left_vline_x == 0 or self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()
            
        self.right_tool_box.line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_tool_box.line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()

    def crop_graphs_on_right(self):
        if self.las is None:
            return
        
        self.clear_graphs()

        self.crop_data_on_right()

        self.update_graphs()

        self.left_tool_box.line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.left_tool_box.line_spinbox_x.setValue(0)
        if self.left_vline_x == 0:
            self.draw_right_line()

        self.right_tool_box.line_spinbox_x.setMaximum(self.right_spinbox_max_value)
        self.right_tool_box.line_spinbox_x.setValue(self.right_spinbox_max_value)
        if self.right_vline_x == self.right_spinbox_max_value:
            self.draw_left_line()

        self.canvas.draw()