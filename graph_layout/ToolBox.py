from PyQt5.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QPushButton
from PyQt5.QtCore import Qt
import numpy as np

class ToolBox(QHBoxLayout):
    def __init__(self, line_type, crop_graphs, update_line):
        super().__init__()

        # Создание кнопки "Обрезать"
        self.cut_button = QPushButton("Обрезать")
        self.cut_button.clicked.connect(crop_graphs)

        # красная линия
        self.line_label_x = QLabel(f"{line_type} линия X: ")
        self.line_label_y = QLabel("")
        self.line_spinbox_x = QSpinBox()
        self.line_spinbox_x.setMaximum(2147483647)
        self.spinbox_max_value = 2147483647
        self.line_spinbox_x.valueChanged.connect(update_line)

        # layout for spinbox
        spinbox_layout = QHBoxLayout()
        spinbox_layout.setContentsMargins(0, 0, 20, 0)
        spinbox_layout.addWidget(self.line_label_x)
        spinbox_layout.addWidget(self.line_spinbox_x)
        spinbox_layout.addWidget(self.line_label_y)

        # btns_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setContentsMargins(20, 0, 0, 0)
        self.addLayout(spinbox_layout)
        self.addWidget(self.cut_button, 0, Qt.AlignmentFlag.AlignRight)

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
        self.line_label_y.setText(label_text)