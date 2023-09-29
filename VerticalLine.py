import numpy as np


class VerticalLine():
    def __init__(self):
        pass
    
    def update_line_label(self, line_pos_x):
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
        self.red_line_label_y.setText(label_text)
        

    def ensure_line_created(self):
        if self.col_num == 2:
            for col_axes in self.axes:
                for ax in col_axes:
                    self.red_line.append(ax.axvline(0, color='red'))
        else:
            for ax in self.axes:
                self.red_line.append(ax.axvline(0, color='red'))


        # if len(self.red_line) == 0:
        #     for ax in self.axes:
        #         self.red_line.append(ax.axvline(0, color='red'))

    def draw_line(self):
        if self.col_num == 2:
            i = 0
            for col_axes in self.axes:
                for ax in col_axes:
                    self.red_line[i].remove()
                    self.red_line[i] = ax.axvline(self.move_x, color='red')
                    i += 1
        else:
            for i, ax in enumerate(self.axes):
                self.red_line[i].remove()
                self.red_line[i] = ax.axvline(self.move_x, color='red')

        # for i, ax in enumerate(self.axes):
        #     self.red_line[i].remove()
        #     self.red_line[i] = ax.axvline(self.move_x, color='red')
        self.canvas.draw()

    def update_line(self, new_value):
        if self.axes is None:
            return
        
        if self.spinbox_max_value + 1 < new_value:
            new_value = self.spinbox_max_value + 1

        if new_value < 0:
            new_value = 0
        
        self.move_x = new_value
        
        self.update_line_label(self.move_x)

        self.draw_red_line()