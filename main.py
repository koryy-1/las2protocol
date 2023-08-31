import os
import lasio
import numpy as np
import pandas as pd
from config import *

from docx_creator import make_docx

from plot_creator import create_plot


def moving_average(data, window_size):
    return pd.Series(data).rolling(window=window_size).mean().iloc[window_size-1:].values

if __name__ == "__main__":
    cwd = os.getcwd().replace("\\", "/")

    print(f'reading {FILENAME}')
    las = lasio.read(f"{cwd}/examples/{FILENAME}", encoding="cp1251")

    serial_number = las.well["SNUM"].value
    date = las.well["DATE"].value
    instrument_name = las.well["NAME"].value

    params = (serial_number, date, instrument_name)
    # print(params)


    print('calculating moving average for RSD and RLD...')
    smoothed_RSD = moving_average(las["RSD"], WINDOW_SIZE)
    smoothed_RLD = moving_average(las["RLD"], WINDOW_SIZE)

    print('creating plots...')
    MF_RSD = create_plot(las["TIME"], smoothed_RSD, "RSD_1")

    MF_RLD = create_plot(las["TIME"], smoothed_RLD, "RLD_1")

    RLD_on_RSD = smoothed_RLD / smoothed_RSD
    MF_RLD_ON_RSD = create_plot(las["TIME"], RLD_on_RSD, "RLD/RSD")

    MF_MT = create_plot(las["TIME"], las["MT"], "TEMPER")

    MEM_FILES = (MF_RSD, MF_RLD, MF_RLD_ON_RSD, MF_MT)


    output_filename = f"{serial_number}_{date}_{instrument_name}"
    print(f'creating {output_filename}.docx...')
    make_docx(output_filename, params, MEM_FILES, picture_size=7)
    
    # las.to_excel('output.xlsx')

    print('Done.')
    os.system('pause')
