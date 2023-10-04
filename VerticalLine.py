import numpy as np


class VerticalLine():
    def __init__(self):
        self.axes: np.flatiter[np.ndarray]

    def set_asex(self, axes: np.flatiter[np.ndarray]):
        self.axes = axes

    def create(self):
        pass


    def update(self):
        pass





    
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
        
        self.draw_red_line()