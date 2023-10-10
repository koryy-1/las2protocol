from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsScene
from PyQt5.QtCore import Qt

import numpy as np
from lasio import LASFile

from models.ColumnData import AbstractColumnData, ColumnDataGamma, ColumnDataNeutronic
from models.GraphData import GraphData
from graph_layout.GraphCanvas import GraphCanvas

class GraphLayout(QHBoxLayout):
    def __init__(self):
        super().__init__()

        self.column_data_gamma = ColumnDataGamma()
        self.column_data_neutronic = ColumnDataNeutronic()

        self.gamma_graph_canvas = GraphCanvas(self.column_data_gamma)
        self.neutronic_graph_canvas = GraphCanvas(self.column_data_neutronic)
        self.addWidget(self.gamma_graph_canvas)
        self.addWidget(self.neutronic_graph_canvas)

        self.is_gamma = False
        self.is_neutronic = False
        self.is_gamma_canvas_visible = True
        self.is_neutronic_canvas_visible = True

    def show_gamma_canvas(self):
        if not self.is_gamma_canvas_visible:
            self.layout().addWidget(self.gamma_graph_canvas)
            self.is_gamma_canvas_visible = not self.is_gamma_canvas_visible

    def hide_gamma_canvas(self):
        if self.is_gamma_canvas_visible:
            self.layout().removeWidget(self.gamma_graph_canvas)
            self.is_gamma_canvas_visible = not self.is_gamma_canvas_visible


    def show_neutronic_canvas(self):
        if not self.is_neutronic_canvas_visible:
            self.layout().addWidget(self.neutronic_graph_canvas)
            self.is_neutronic_canvas_visible = not self.is_neutronic_canvas_visible

    def hide_neutronic_canvas(self):
        if self.is_neutronic_canvas_visible:
            self.layout().removeWidget(self.neutronic_graph_canvas)
            self.is_neutronic_canvas_visible = not self.is_neutronic_canvas_visible


    def set_las(self, las: LASFile):
        self.clear_canvases()
        # self.hide_gamma_canvas()
        # self.hide_neutronic_canvas()
        self.define_device_type(las)
        if self.is_gamma:
            # self.show_gamma_canvas()
            self.gamma_graph_canvas.set_las(las)
        if self.is_neutronic:
            # self.show_neutronic_canvas()
            self.neutronic_graph_canvas.set_las(las)

    def clear_canvases(self):
        self.gamma_graph_canvas.clear()
        self.neutronic_graph_canvas.clear()

    def set_is_gamma(self, is_gamma):
        self.is_gamma = is_gamma

    def set_is_neutronic(self, is_neutronic):
        self.is_neutronic = is_neutronic

    def define_device_type(self, las: LASFile):
        self.set_is_gamma("RSD" in las.keys())
        self.set_is_neutronic("NTNC" in las.keys())

    def set_size_entry(self, size_entry):
        self.gamma_graph_canvas.set_size_entry(size_entry)
        self.neutronic_graph_canvas.set_size_entry(size_entry)

    def set_smooth_count_entry(self, smooth_count_entry):
        self.gamma_graph_canvas.set_smooth_count_entry(smooth_count_entry)
        self.neutronic_graph_canvas.set_smooth_count_entry(smooth_count_entry)

    def plot_graphs(self):
        if self.is_gamma:
            self.gamma_graph_canvas.plot_graphs()
        if self.is_neutronic:
            self.neutronic_graph_canvas.plot_graphs()