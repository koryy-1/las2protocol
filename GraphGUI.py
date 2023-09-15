import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GraphGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Выбор и перетаскивание точки")

        # Создание объекта Figure и осей графика
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Создание графического холста
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Создание кнопки "Выбрать точку"
        self.select_button = tk.Button(self.root, text="Выбрать точку", command=self.select_point)
        self.select_button.pack(side=tk.BOTTOM)

        # Переменные для хранения координат точки на графике
        self.x = 0
        self.y = 0

        # массивы для отрисовки графика
        self.x_arr = []
        self.y_arr = []

    def plot_graph(self):
        # Очистка графика
        self.ax.clear()

        # Рисование графика
        self.ax.plot(self.x_arr, self.y_arr)

        # Рисование крестика в выбранной точке
        self.ax.plot(self.x, self.y, marker='|', markersize=100, color='red')

        # Обновление графического холста
        self.canvas.draw()

    def select_point(self):
        # Функция для обработки события нажатия на точку на графике
        def onclick(event):
            self.x = event.xdata
            self.y = event.ydata
            self.plot_graph()

        # Подключение обработчика события нажатия на точку
        self.canvas.mpl_connect('button_press_event', onclick)

    def run(self):
        self.plot_graph()
        tk.mainloop()
