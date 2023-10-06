from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt5.QtCore import Qt
import numpy as np

from models.GraphData import GraphData
from models.ColumnData import AbstractColumnData

class ToolBox(QHBoxLayout):
    def __init__(self, crop_graphs, update_left_line, update_right_line):
        super().__init__()

        # Создание кнопки "Обрезать"
        self.cut_button = QPushButton("Обрезать")
        self.cut_button.clicked.connect(crop_graphs)

        # left line
        self.left_line_label_x = QLabel(f"Левая линия X: ")
        self.left_line_label_y = QLabel("")
        self.left_line_spinbox_x = QSpinBox()
        self.left_line_spinbox_x.setMaximum(2147483647)
        self.left_spinbox_max_value = 2147483647
        self.left_line_spinbox_x.valueChanged.connect(update_left_line)
        # layout for spinbox
        left_line_spinbox_layout = QHBoxLayout()
        left_line_spinbox_layout.setContentsMargins(0, 0, 20, 0)
        left_line_spinbox_layout.addWidget(self.left_line_label_x)
        left_line_spinbox_layout.addWidget(self.left_line_spinbox_x)
        left_line_spinbox_layout.addWidget(self.left_line_label_y)

        # right line
        self.right_line_label_x = QLabel(f"Правая линия X: ")
        self.right_line_label_y = QLabel("")
        self.right_line_spinbox_x = QSpinBox()
        self.right_line_spinbox_x.setMaximum(2147483647)
        self.right_spinbox_max_value = 2147483647
        self.right_line_spinbox_x.valueChanged.connect(update_right_line)
        # layout for spinbox
        right_line_spinbox_layout = QHBoxLayout()
        right_line_spinbox_layout.setContentsMargins(0, 0, 20, 0)
        right_line_spinbox_layout.addWidget(self.right_line_label_x)
        right_line_spinbox_layout.addWidget(self.right_line_spinbox_x)
        right_line_spinbox_layout.addWidget(self.right_line_label_y)

        # btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setContentsMargins(20, 0, 0, 0)
        self.addLayout(left_line_spinbox_layout)
        self.addLayout(right_line_spinbox_layout)
        self.addWidget(self.cut_button, 0, Qt.AlignmentFlag.AlignRight)

    def update_line_label(self, graph_data: GraphData, column_data: AbstractColumnData, line_pos_x):
        NEAR_PROBE_Y = int(np.round(graph_data.near_probe[line_pos_x]))
        FAR_PROBE_Y = int(np.round(graph_data.far_probe[line_pos_x]))
        FAR_ON_NEAR_PROBE_Y = np.round(graph_data.far_on_near_probe[line_pos_x], 3)
        TEMPER_Y = int(graph_data.temper[line_pos_x])

        return f'\t{column_data.near_probe} Y: {NEAR_PROBE_Y}\t{column_data.far_probe} Y: {FAR_PROBE_Y}\t{column_data.far_probe}/{column_data.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'

    # def update_left_line_label(self, gamma_graph_data, column_data_gamma, line_pos_x):
    #     label_text = ''
    #     if is_gamma:
    #         NEAR_PROBE_Y = int(np.round(gamma_graph_data.near_probe[line_pos_x]))
    #         FAR_PROBE_Y = int(np.round(gamma_graph_data.far_probe[line_pos_x]))
    #         FAR_ON_NEAR_PROBE_Y = np.round(gamma_graph_data.far_on_near_probe[line_pos_x], 3)
    #         TEMPER_Y = int(gamma_graph_data.temper[line_pos_x])
    #         label_text = f'\t{column_data_gamma.near_probe} Y: {NEAR_PROBE_Y}\t{column_data_gamma.far_probe} Y: {FAR_PROBE_Y}\t{column_data_gamma.far_probe}/{column_data_gamma.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
    #     if is_neutronic:
    #         NEAR_PROBE_Y = int(np.round(neutronic_graph_data.near_probe[line_pos_x]))
    #         FAR_PROBE_Y = int(np.round(neutronic_graph_data.far_probe[line_pos_x]))
    #         FAR_ON_NEAR_PROBE_Y = np.round(neutronic_graph_data.far_on_near_probe[line_pos_x], 3)
    #         TEMPER_Y = int(neutronic_graph_data.temper[line_pos_x])
    #         label_text = label_text + f'\t{column_data_neutronic.near_probe} Y: {NEAR_PROBE_Y}\t{column_data_neutronic.far_probe} Y: {FAR_PROBE_Y}\t{column_data_neutronic.far_probe}/{column_data_neutronic.near_probe} Y: {FAR_ON_NEAR_PROBE_Y}\tTEMPER Y: {TEMPER_Y}'
    #     self.line_label_y.setText(label_text)