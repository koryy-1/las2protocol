from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QFileDialog, QLabel, QCheckBox, QRadioButton, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
import lasio

from GraphCanvas import GraphCanvas
from models.ColumnData import ColumnDataGamma, ColumnDataNeutronic
from models.GraphData import GraphData
from process_sample import save2doc

class SidePanel(QVBoxLayout):
    def __init__(self, las_file_analyzer, graph_canvas: GraphCanvas):
        super().__init__()

        self.graph_canvas = graph_canvas

        self.las_file_analyzer = las_file_analyzer

        self.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Размер окна
        DURATION_1_COUNT = 4000
        self.size_entry = QLineEdit()
        self.size_entry.setText(str(int(4 * 60 * 1000 / DURATION_1_COUNT)))
        self.size_entry.textChanged.connect(self.graph_canvas.set_size_entry)

        # Количество применений функции сглаживания
        self.smooth_count_entry = QLineEdit()
        self.smooth_count_entry.setText("3")
        self.smooth_count_entry.textChanged.connect(self.graph_canvas.set_smooth_count_entry)

        # Часть графика для обработки
        self.process_heat_checkbox = QCheckBox("Нагрев")
        self.process_heat_checkbox.setChecked(True)
        self.process_cool_checkbox = QCheckBox("Охлаждение")
        self.process_cool_checkbox.setChecked(True)
        # Тип прибора
        # todo: change radio btn on label
        self.device_type_gamma_radio_btn = QRadioButton("Gamma")
        self.device_type_gamma_radio_btn.setChecked(True)

        self.device_type_neutronic_radio_btn = QRadioButton("Neutronic")
        
        # Создаем виджет для параметров с использованием QFormLayout
        form_layout = QFormLayout()
        form_layout.addRow("Размер окна:", self.size_entry)
        form_layout.addRow("Количество применений сглаживания:", self.smooth_count_entry)
        form_layout.addRow("Какую часть графика обрабатывать:", self.process_heat_checkbox)
        form_layout.addRow("", self.process_cool_checkbox)
        form_layout.addRow("Тип прибора:", self.device_type_gamma_radio_btn)
        form_layout.addRow("", self.device_type_neutronic_radio_btn)
        self.addLayout(form_layout)

        # Кнопка открытия .las файла
        self.open_button = QPushButton("Открыть .las файл")
        self.open_button.clicked.connect(self.open_las_file)
        self.addWidget(self.open_button)

        # Метка для вывода пути до файла
        self.file_path_label = QLabel("")
        self.addWidget(self.file_path_label)

        # Кнопка построения графиков
        self.plot_button = QPushButton("Построить графики")
        self.plot_button.clicked.connect(self.graph_canvas.plot_graphs)
        self.addWidget(self.plot_button)

        # Кнопка показать расчеты
        self.show_calculations_button = QPushButton("Показать расчеты")
        # self.show_calculations_button.clicked.connect(self.show_calculations)
        self.addWidget(self.show_calculations_button)

        # Кнопка сохранения в .docx файл
        self.save_button = QPushButton("Сохранить в .docx файл")
        self.save_button.clicked.connect(self.save_to_docx)
        self.addWidget(self.save_button)
        self.success_label = QLabel("")
        self.addWidget(self.success_label)

        # self.save_excel_button
        # las.to_excel('output.xlsx')

    def open_las_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self.las_file_analyzer, "Открыть .las файл", "", "LAS Files (*.las)", options=options)
        if file_path:
            self.file_path_label.setText(file_path.split("/")[-1])
            self.graph_canvas.set_las(lasio.read(file_path, encoding="cp1251"))

            self.graph_canvas.define_device_type()

            self.graph_canvas.plot_graphs()


    def save_to_docx(self):
        if self.graph_canvas.is_gamma:
            titles = ColumnDataGamma.near_probe, ColumnDataGamma.far_probe
            self.save_to_separate_docx(self.graph_canvas.gamma_graph_data, titles)
            
        if self.graph_canvas.is_neutronic:
            titles = ColumnDataNeutronic.near_probe, ColumnDataNeutronic.far_probe
            self.save_to_separate_docx(self.graph_canvas.neutronic_graph_data, titles)

    def save_to_separate_docx(self, data: GraphData, titles):
        if self.graph_canvas.las is None:
            return

        self.success_label.setText("processing...")

        # serial_number = self.graph_canvas.las.well["SNUM"].value
        serial_number = 'self.graph_canvas.las.well["SNUM"].value'
        date = self.graph_canvas.las.well["DATE"].value
        # instrument_name = self.graph_canvas.las.well["NAME"].value
        instrument_name = 'self.graph_canvas.las.well["NAME"].value'

        description = (serial_number, date, instrument_name)

        thresholds = (
            data.near_probe_threshold,
            data.far_probe_threshold
        )

        success = save2doc(
            int(self.size_entry.text()),
            bool(self.process_heat_checkbox.isChecked()),
            bool(self.process_cool_checkbox.isChecked()),
            description,
            data,
            titles,
            thresholds
        )

        if success:
            self.success_label.setText("docx saved successfully")
        else:
            self.success_label.setText("ERROR: failed to save docx")