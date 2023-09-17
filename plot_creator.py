from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_plot(x, y, plot_title: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(12, 3.5))
    
    ax.plot(y, label=plot_title)
    ax.set_ylim(y.min() * 0.9, y.max() * 1.1)
    ax.set_xlim(-200, len(x) * 1.2)

    ax.legend([plot_title], loc='right')

    plt.grid(True)

    plt.title(plot_title)

    memfile = BytesIO()
    fig.savefig(memfile)

    return memfile


def create_plot_on_canvas(ax, x, y, plot_title: str):
    ax.plot(y, label=plot_title)
    ax.set_ylim(y.min() * 0.9, y.max() * 1.1)
    ax.set_xlim(-200, len(x) * 1.2)

    ax.legend([plot_title], loc='right')
