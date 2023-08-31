import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create_plot(x, y, plot_title: str, filename: str):
    # my_dict = dict(x, y)

    # data = pd.DataFrame (my_dict)
    # plt.style.use("Solarize_Light2")

    fig, ax = plt.subplots(figsize=(10, 4))
    
    ax.plot(y, label=plot_title)
    ax.set_ylim(1, y.max() * 1.5) 

    ax.legend(y, loc='right')

    plt.grid(True)

    plt.title(plot_title)
    fig.savefig(f"{filename}.png", dpi=200,)
    # plt.show()