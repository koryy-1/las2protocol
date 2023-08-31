import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def create(my_dict: dict, plot_title: str, filename: str):
    data = pd.DataFrame (my_dict)
    fig, ax = plt.subplots()
    ax = sns.barplot(x='x', y='y', data=data, )
    ax.set_title(plot_title)

    # plt.legend(loc='upper right')

    fig.savefig(f"{filename}.png", dpi=200, orientation='landscape')
    # plt.show()