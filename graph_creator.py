from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def create_graph(x, y, plot_title: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(12, 3.5))
    
    ax.plot(y, label=plot_title)
    # ax.set_ylim(y.min() * 0.9, y.max() * 1.1)
    ax.set_xlim(-(len(x) * 0.02), len(x) * 1.23)

    ax.legend([plot_title], loc='right')

    plt.grid(True)

    plt.title(plot_title)

    memfile = BytesIO()
    fig.savefig(memfile)

    return memfile


def create_graph_on_canvas(ax, x, y, plot_title: str):
    # print(plot_title, y)
    ax.grid(True)
    ax.plot(y, label=plot_title)
    # ax.set_ylim(y.min() * 0.9, y.max() * 1.1)
    ax.set_xlim(-(len(x) * 0.02), len(x) * 1.23)

    ax.legend(loc='right')
