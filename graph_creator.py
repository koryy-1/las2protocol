from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def create_graph(x, y, plot_title: str) -> BytesIO:
    fig, ax = plt.subplots(figsize=(12, 3.5))
    
    ax.plot(y, label=plot_title, linewidth=2)

    fontsize = 14

    ax.xaxis.set_tick_params(labelsize=fontsize, width=1, pad=8)
    ax.yaxis.set_tick_params(labelsize=fontsize, width=1, pad=8)

    ax.xaxis.grid(True, linewidth=1, alpha=1, color='black')
    ax.yaxis.grid(True, linewidth=1, alpha=1, color='black')

    ax.legend(loc='right', fontsize=fontsize)

    try:
        ax.set_ylim(y[np.isfinite(y)].min() * 0.9, y[np.isfinite(y)].max() * 1.1)
    except:
        print(f"no {plot_title}")
    ax.set_xlim(-(len(x) * 0.02), len(x) * 1.23)

    memfile = BytesIO()
    fig.savefig(memfile)

    return memfile
