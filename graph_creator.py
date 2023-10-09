from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def create_graph(x, y, plot_title: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(12, 3.5))
    
    fontsize = 12
    plt.rc('font', size=fontsize) #controls default text size
    plt.rc('axes', titlesize=fontsize) #fontsize of the title
    plt.rc('axes', labelsize=fontsize) #fontsize of the x and y labels
    plt.rc('xtick', labelsize=fontsize) #fontsize of the x tick labels
    plt.rc('ytick', labelsize=fontsize) #fontsize of the y tick labels
    plt.rc('legend', fontsize=fontsize) #fontsize of the legend

    ax.plot(y, label=plot_title)
    try:
        ax.set_ylim(y[np.isfinite(y)].min() * 0.9, y[np.isfinite(y)].max() * 1.1)
    except:
        print(f"no {plot_title}")
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
    ax.set_ylim(y[np.isfinite(y)].min() * 0.9, y[np.isfinite(y)].max() * 1.1)
    ax.set_xlim(-(len(x) * 0.02), len(x) * 1.23)

    ax.legend(loc='right')
