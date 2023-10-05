import numpy as np


class VerticalLine():
    def __init__(self):
        self.axes: np.flatiter[np.ndarray]

    def set_axes(self, axes: np.flatiter[np.ndarray]):
        self.axes = axes

    def create(self):
        pass


    def set_X(self):
        pass


    def on_mouse_press(self, event):
        if event.button == 1 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.left_dragging = True

            self.left_vline_x = int(event.xdata)
            self.update_left_line(self.left_vline_x)

        if event.button == 3 and event.xdata is not None:  # Проверяем, что нажата левая кнопка мыши
            # print("press", int(event.xdata))
            self.right_dragging = True

            self.right_vline_x = int(event.xdata)
            self.update_right_line(self.right_vline_x)

    def on_mouse_move(self, event):
        if self.left_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.left_vline_x = int(event.xdata)
            self.update_left_line(self.left_vline_x)

        if self.right_dragging and event.xdata is not None:
            # print("move xdata", int(event.xdata))

            self.right_vline_x = int(event.xdata)
            self.update_right_line(self.right_vline_x)

    def on_mouse_release(self, event):
        if self.left_dragging:
            self.left_dragging = False
            # print("release", int(event.xdata))

        if self.right_dragging:
            self.right_dragging = False
            # print("release", int(event.xdata))

    



    
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
        
        self.draw_line()