import os
import sys
import glob
import lasio
import datetime
import numpy as np
import pandas as pd
from calculations import *

from docx_creator import make_docx

from plot_creator import create_plot


def moving_average(data, window_size):
    return pd.Series(data).rolling(window=window_size).mean().iloc[window_size-1:].values


if __name__ == "__main__":
    cwd = os.getcwd().replace("\\", "/")

    FILENAME = glob.glob('*.las')[0]

    print(f'reading {FILENAME}')
    try:
        las = lasio.read(f"{cwd}/{FILENAME}", encoding="cp1251")
    except:
        print(f'ERROR: file {FILENAME} not found')
        sys.exit() 
        

    serial_number = las.well["SNUM"].value
    date = las.well["DATE"].value
    instrument_name = las.well["NAME"].value

    
    DURATION_1_COUNT = 4000
    WINDOW_SIZE = int(4 * 60 * 1000 / DURATION_1_COUNT)
    print('WINDOW_SIZE', WINDOW_SIZE)
    
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

    ######
    # print(find_temperature_rise_point_right(las["MT"], 1))

    # choice: 1 - for heating, 2 - for cooling
    heating_table = get_calculation_table(1, WINDOW_SIZE, las["MT"][:np.argmax(las["MT"])], smoothed_RSD, smoothed_RLD, RLD_on_RSD)

    # проделать вычисления для охлада
    # для охлада базовая темп = последний минимум
    # find_temperature_drop_point вычисляет точку в которой функция температуры начинает идти вниз
    T_max_index, T_max = find_temperature_drop_point(las["MT"], 2)
    cooling_table = get_calculation_table(2, WINDOW_SIZE, las["MT"][T_max_index:], smoothed_RSD, smoothed_RLD, RLD_on_RSD)

    conclusion = get_conclusion(heating_table)
    conclusion = get_conclusion(heating_table) ###

    params = (
        serial_number, 
        date, 
        instrument_name, 
        heating_table, 
        cooling_table, 
        conclusion, 
        las["MT"].min(), 
        las["MT"].max(),
        las["ADCS"][0],
        las["ADCL"][0],
        )
    # print(params)

 
    current_date = datetime.datetime.now().strftime('%d%m%y')
    output_filename = f"{serial_number}_{instrument_name}_{current_date}_by_program"
    print(f'creating {output_filename}.docx...')
    success = make_docx(output_filename, params, MEM_FILES, picture_size=6.5)

    if (success):
        print('docx successfully saved')
        print('Done.')
    else:
        print()
        print(f'ERROR: failed to save, please close document {output_filename}.docx')
    

    # las.to_excel('output.xlsx')

    os.system('pause')
