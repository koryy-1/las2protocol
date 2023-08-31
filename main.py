import os
import lasio
import numpy as np

from docx_creator import make_docx

from plot_creator import create_plot

if __name__ == "__main__":
    # fulPath = r"C:/Users/Андрей/Desktop/Ilya/19399001 2023-07-27 09-46-50 ГГКП.rt.las"
    # print(fulPath)
    cwd = os.getcwd().replace("\\", "/")

    filename = "19399001 2023-07-27 09-46-50 ГГКП.rt.las"
    las = lasio.read(f"{cwd}/examples/{filename}")
    Keys=las.keys()
    print(Keys)
    print(os.getcwd())


    # smoothing
    # smoothed_RSD = [for]
    create_plot(las["TIME"], las["RSD"], "RSD_1", "RSD")

    create_plot(las["TIME"], las["RLD"], "RLD_1", "RLD")

    RSD_y = las["RSD"]
    RLD_on_RSD = [el/RSD_y[8] for el in RSD_y]
    create_plot(las["TIME"], np.array(RLD_on_RSD), "RLD/RSD", "RLD_on_RSD")

    create_plot(las["TIME"], las["MT"], "TEMPER", "TEMPER")

    make_docx()

    # las.to_excel('output.xlsx')