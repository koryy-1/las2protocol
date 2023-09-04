import os
import sys
import glob
import lasio
import datetime
import numpy as np
import pandas as pd
from calculations import get_calculation_table, get_conclusion

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

    
    print('calculating moving average for RSD and RLD...')
    WINDOW_SIZE = 120
    smoothed_RSD = moving_average(las["RSD"], WINDOW_SIZE)
    smoothed_RLD = moving_average(las["RLD"], WINDOW_SIZE)

    print('creating plots...')
    MF_RSD = create_plot(las["TIME"], smoothed_RSD, "RSD_1")

    MF_RLD = create_plot(las["TIME"], smoothed_RLD, "RLD_1")

    RLD_on_RSD = smoothed_RLD / smoothed_RSD
    MF_RLD_ON_RSD = create_plot(las["TIME"], RLD_on_RSD, "RLD/RSD")

    MF_MT = create_plot(las["TIME"], las["MT"], "TEMPER")

    MEM_FILES = (MF_RSD, MF_RLD, MF_RLD_ON_RSD, MF_MT)

    table = get_calculation_table(las["MT"], smoothed_RSD, smoothed_RLD, RLD_on_RSD)

    conclusion = get_conclusion(table)

    params = (
        serial_number, 
        date, 
        instrument_name, 
        table, 
        conclusion, 
        las["MT"].min(), 
        las["MT"].max(),
        las["ADCS"][0],
        las["ADCL"][0],
        )
    # print(params)

 
    current_date = datetime.datetime.now().strftime('%d%m%y')
    output_filename = f"{serial_number}_{instrument_name}_{current_date}"
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
