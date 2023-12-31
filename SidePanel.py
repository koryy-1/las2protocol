from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QFileDialog, QLabel, QCheckBox, QRadioButton, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
import lasio
from MultiTableWindow import MultiTableWindow

from graph_layout.GraphLayout import GraphLayout
from models.ColumnData import ColumnDataGamma, ColumnDataNeutronic
from models.GraphData import GraphData
from process_sample import get_calc_for_tables, save2doc
from utils import find_temperature_drop_point

class SidePanel(QVBoxLayout):
    def __init__(self, las_file_analyzer, graph_layout: GraphLayout):
        super().__init__()

        self.graph_layout = graph_layout

        self.las_file_analyzer = las_file_analyzer

        self.column_data_gamma = ColumnDataGamma()
        self.column_data_neutronic = ColumnDataNeutronic()

        self.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Размер окна
        DURATION_1_COUNT = 4000
        self.size_entry = QLineEdit()
        self.size_entry.setText(str(int(4 * 60 * 1000 / DURATION_1_COUNT)))
        self.size_entry.textChanged.connect(self.graph_layout.set_size_entry)
        self.graph_layout.set_size_entry(self.size_entry.text())

        # Количество применений функции сглаживания
        self.smooth_count_entry = QLineEdit()
        self.smooth_count_entry.setText("3")
        self.smooth_count_entry.textChanged.connect(self.graph_layout.set_smooth_count_entry)
        self.graph_layout.set_smooth_count_entry(self.smooth_count_entry.text())

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

        self.is_clear_graph_checkbox = QCheckBox("")
        self.is_clear_graph_checkbox.setChecked(True)
        self.is_clear_graph_checkbox.stateChanged.connect(self.graph_layout.set_is_clear_graphs)
        
        # Создаем виджет для параметров с использованием QFormLayout
        form_layout = QFormLayout()
        form_layout.addRow("Размер окна:", self.size_entry)
        form_layout.addRow("Кол-во прим сглаж:", self.smooth_count_entry)
        form_layout.addRow("Обработать:", self.process_heat_checkbox)
        form_layout.addRow("", self.process_cool_checkbox)
        form_layout.addRow("Какие данные сохранить:", self.device_type_gamma_radio_btn)
        form_layout.addRow("", self.device_type_neutronic_radio_btn)
        form_layout.addRow("Очищать график при постр:", self.is_clear_graph_checkbox)
        self.addLayout(form_layout)

        # Кнопка открытия .las файла
        self.open_button = QPushButton("Открыть .las файл")
        self.open_button.clicked.connect(self.open_las_file)
        self.addWidget(self.open_button)

        # Метка для вывода пути до файла
        self.file_path_label = QLabel("")
        self.addWidget(self.file_path_label)

        # Кнопка построения графиков
        self.plot_button = QPushButton("Перестроить графики")
        self.plot_button.clicked.connect(self.graph_layout.plot_graphs)
        self.addWidget(self.plot_button)

        # Кнопка отметить экстремумы и базовую точку функции
        self.mark_extreme_points_button = QPushButton("Отметить экстремумы")
        self.mark_extreme_points_button.clicked.connect(self.mark_extreme_points)
        self.addWidget(self.mark_extreme_points_button)

        # Кнопка показать расчеты
        self.show_calculations_button = QPushButton("Показать расчеты")
        self.show_calculations_button.clicked.connect(self.show_calculations)
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
            self.graph_layout.set_las(lasio.read(file_path, encoding="cp1251"))
            self.graph_layout.plot_graphs()

    def mark_extreme_points(self):
        self.graph_layout.mark_extreme_points(
            self.process_heat_checkbox.isChecked(),
            self.process_cool_checkbox.isChecked()
        )


    def show_calculations(self):
        datas = []
        rows = 0
        cols = 0
        if self.process_heat_checkbox.isChecked():
            rows += 1
        if self.process_cool_checkbox.isChecked():
            rows += 1

        if self.graph_layout.is_gamma:
            cols += 1
            is_heat = self.process_heat_checkbox.isChecked()
            is_cool = self.process_cool_checkbox.isChecked()
            T_max_index, _ = find_temperature_drop_point(self.graph_layout.gamma_graph_canvas.graph_data.temper, 2)
            
            if not T_max_index:
                print('program not defined boundaries beetwen heating and cooling')
                print('may be temperature function only show heating')
                is_cool = False

            (heating_table, cooling_table) = get_calc_for_tables(
                is_heat,
                is_cool,
                int(self.size_entry.text()),
                T_max_index,
                self.graph_layout.gamma_graph_canvas.graph_data.temper,  
                self.graph_layout.gamma_graph_canvas.graph_data.near_probe, 
                self.graph_layout.gamma_graph_canvas.graph_data.far_probe, 
                self.graph_layout.gamma_graph_canvas.graph_data.far_on_near_probe
            )
            datas.append((heating_table, cooling_table, self.column_data_gamma))

        if self.graph_layout.is_neutronic:
            cols += 1
            is_heat = self.process_heat_checkbox.isChecked()
            is_cool = self.process_cool_checkbox.isChecked()
            T_max_index, _ = find_temperature_drop_point(self.graph_layout.neutronic_graph_canvas.graph_data.temper, 2)
            
            if not T_max_index:
                print('program not defined boundaries beetwen heating and cooling')
                print('may be temperature function only show heating')
                is_cool = False

            (heating_table, cooling_table) = get_calc_for_tables(
                is_heat,
                is_cool,
                int(self.size_entry.text()),
                T_max_index,
                self.graph_layout.neutronic_graph_canvas.graph_data.temper,  
                self.graph_layout.neutronic_graph_canvas.graph_data.near_probe, 
                self.graph_layout.neutronic_graph_canvas.graph_data.far_probe, 
                self.graph_layout.neutronic_graph_canvas.graph_data.far_on_near_probe
            )
            datas.append((heating_table, cooling_table, self.column_data_neutronic))
        
        self.multi_table_window = MultiTableWindow(datas, rows, cols)
        self.multi_table_window.show()


    def save_to_docx(self):
        if self.graph_layout.is_gamma and self.graph_layout.is_neutronic:
            if self.device_type_gamma_radio_btn.isChecked():
                titles = self.column_data_gamma.near_probe, self.column_data_gamma.far_probe
                serial_number = '12345'
                date = self.graph_layout.gamma_graph_canvas.las.well["DATE"].value
                instrument_name = 'ГГКП'
                self.save_to_separate_docx(
                    self.graph_layout.gamma_graph_canvas.las is None,
                    self.graph_layout.gamma_graph_canvas.graph_data, 
                    titles,
                    self.process_heat_checkbox.isChecked(),
                    self.process_cool_checkbox.isChecked(),
                    (serial_number, date, instrument_name)
                )
                
            if self.device_type_neutronic_radio_btn.isChecked():
                titles = self.column_data_neutronic.near_probe, self.column_data_neutronic.far_probe
                serial_number = '12345'
                date = self.graph_layout.neutronic_graph_canvas.las.well["DATE"].value
                instrument_name = 'ННКТ'
                self.save_to_separate_docx(
                    self.graph_layout.neutronic_graph_canvas.las is None,
                    self.graph_layout.neutronic_graph_canvas.graph_data, 
                    titles,
                    self.process_heat_checkbox.isChecked(),
                    self.process_cool_checkbox.isChecked(),
                    (serial_number, date, instrument_name)
                )
            return


        if self.graph_layout.is_gamma:
            titles = self.column_data_gamma.near_probe, self.column_data_gamma.far_probe
            serial_number = self.graph_layout.gamma_graph_canvas.las.well["SNUM"].value
            date = self.graph_layout.gamma_graph_canvas.las.well["DATE"].value
            instrument_name = self.graph_layout.gamma_graph_canvas.las.well["NAME"].value
            self.save_to_separate_docx(
                self.graph_layout.gamma_graph_canvas.las is None,
                self.graph_layout.gamma_graph_canvas.graph_data, 
                titles,
                self.process_heat_checkbox.isChecked(),
                self.process_cool_checkbox.isChecked(),
                (serial_number, date, instrument_name)
            )
            
        if self.graph_layout.is_neutronic:
            titles = self.column_data_neutronic.near_probe, self.column_data_neutronic.far_probe
            serial_number = self.graph_layout.neutronic_graph_canvas.las.well["SNUM"].value
            date = self.graph_layout.neutronic_graph_canvas.las.well["DATE"].value
            instrument_name = self.graph_layout.neutronic_graph_canvas.las.well["NAME"].value
            self.save_to_separate_docx(
                self.graph_layout.neutronic_graph_canvas.las is None,
                self.graph_layout.neutronic_graph_canvas.graph_data, 
                titles,
                self.process_heat_checkbox.isChecked(),
                self.process_cool_checkbox.isChecked(),
                (serial_number, date, instrument_name)
            )

    def save_to_separate_docx(self, las_is_none, data: GraphData, titles, process_heat, process_cool, description):
        if las_is_none:
            return

        self.success_label.setText("processing...")

        # serial_number = self.graph_canvas.las.well["SNUM"].value
        # date = self.graph_layout.las.well["DATE"].value
        # instrument_name = self.graph_canvas.las.well["NAME"].value

        thresholds = (
            data.near_probe_threshold,
            data.far_probe_threshold
        )

        success = save2doc(
            int(self.size_entry.text()),
            process_heat,
            process_cool,
            description,
            data,
            titles,
            thresholds
        )

        if success:
            self.success_label.setText("docx saved successfully")
        else:
            self.success_label.setText("ERROR: failed to save docx")