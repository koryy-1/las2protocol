from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt

class SidePanel(QVBoxLayout):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        
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
        self.plot_button.clicked.connect(self.plot_graphs)
        self.addWidget(self.plot_button)

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