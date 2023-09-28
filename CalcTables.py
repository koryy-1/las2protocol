from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtCore import Qt

from process_sample import get_calc_for_tables
from utils import find_temperature_drop_point

class CalcTables(QVBoxLayout):
    def __init__(self):
        super().__init__()

        # todo: create 2 tables for heat and cool


    def show_calculations(self):
        if self.las is None:
            return

        is_heating = self.process_heat_checkbox.isChecked()
        is_cooling = self.process_cool_checkbox.isChecked()
        window_size = int(self.size_entry.text())

        T_max_index, _ = find_temperature_drop_point(self.gamma_graph_data.temper, 2)
        if not T_max_index:
            print('program not defined boundaries beetwen heating and cooling')
            print('may be temperature function only show heating')
            is_cooling = False

        heating_table, cooling_table = get_calc_for_tables(
            is_heating, is_cooling, window_size, T_max_index,
            self.gamma_graph_data.temper, self.gamma_graph_data.near_probe,
            self.gamma_graph_data.far_probe, self.gamma_graph_data.far_on_near_probe
        )

        if is_heating:
            self.show_table("Расчеты для нагрева", heating_table)

        if is_cooling:
            self.show_table("Расчеты для охлаждения", cooling_table)

    def show_table(self, title, data):
        print(title)
        print(data)