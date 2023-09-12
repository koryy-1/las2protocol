import os
import sys
import glob
import lasio
import datetime
import numpy as np
from calculations import *

from docx_creator import make_docx

from plot_creator import create_plot

def get_calc_for_tables(
        plot_part: int,
        window_size: int,
        TEMPER: np.ndarray,  
        smoothed_RSD: np.ndarray, 
        smoothed_RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray
        ):
    heating_table = None
    cooling_table = None
    if plot_part == 1 or plot_part == 2:
        heating_table = get_calculation_table(
            1, 
            window_size, 
            TEMPER[:T_max_index], 
            smoothed_RSD[:T_max_index], 
            smoothed_RLD[:T_max_index], 
            RLD_on_RSD[:T_max_index]
            )

    # проделать вычисления для охлада
    # для охлада базовая темп = последний минимум
    # print(las["MT"][T_max_index:])
    if plot_part == 1 or plot_part == 3:
        cooling_table = get_calculation_table(
            2, 
            window_size, 
            TEMPER[T_max_index:], 
            smoothed_RSD[T_max_index:], 
            smoothed_RLD[T_max_index:], 
            RLD_on_RSD[T_max_index:]
            )
    
    return heating_table, cooling_table

def get_conclusion(heating_table, cooling_table):
    if (
        (heating_table and exceeds_threshold(heating_table))
        or
        (cooling_table and exceeds_threshold(cooling_table))
        ):
        return 'превышает'
    else:
        return 'не превышает'
    
def get_filename_las():
    filenames = glob.glob('*.las')
    if len(filenames) > 1:
        print('Выберите, c какого файла считать данные:')
        for i in range(len(filenames)):
            print(f'{i + 1} - \"{filenames[i]}\"')
        choosed_file = int(input('> '))
        return filenames[choosed_file-1]
    else:
        return filenames[0]


if __name__ == "__main__":
    DURATION_1_COUNT = 4000
    window_size = int(4 * 60 * 1000 / DURATION_1_COUNT)
    # print('WINDOW_SIZE', WINDOW_SIZE)
    # 1 - heat and cool, 2 - only heat, 3 - only cool
    plot_part = 1
    moving_average_count = 3

    while True:
        print('Выберите действие:')
        print('1 - составить протокол')
        print('2 - выбрать промежуток графика температуры для расчетов')
        print('3 - изменить параметры')
        choice = int(input('> '))
        if choice == 1:
            break
        if choice == 2:
            print('Выберите промежуток:')
            print('1 - нагрев и охлаждение')
            print('2 - только нагрев')
            print('3 - только охлаждение')
            plot_part = int(input('> '))
        if choice == 3:
            print('Что изменить?')
            print('1 - размер окна')
            print('2 - сколько раз применять функцию сглаживания')
            choice2 = int(input('> '))
            if choice2 == 1:
                print('Введите размер окна:')
                window_size = int(input('> '))
            if choice2 == 2:
                print('Введите кол-во разов:')
                moving_average_count = int(input('> '))
                

    cwd = os.getcwd().replace("\\", "/")
    filename = get_filename_las()

    print(f'reading {filename}')
    try:
        las = lasio.read(f"{cwd}/{filename}", encoding="cp1251")
    except:
        print(f'ERROR: file {filename} not found')
        sys.exit()
        

    serial_number = las.well["SNUM"].value
    date = las.well["DATE"].value
    instrument_name = las.well["NAME"].value

    
    print('calculating moving average for RSD and RLD...')
    smoothed_RSD = moving_average(las["RSD"], window_size, moving_average_count)
    
    smoothed_RLD = moving_average(las["RLD"], window_size, moving_average_count)


    print('creating plots...')
    MF_RSD = create_plot(las["TIME"], smoothed_RSD, "RSD_1")

    MF_RLD = create_plot(las["TIME"], smoothed_RLD, "RLD_1")

    RLD_on_RSD = smoothed_RLD / smoothed_RSD
    MF_RLD_ON_RSD = create_plot(las["TIME"], RLD_on_RSD, "RLD/RSD")

    MF_MT = create_plot(las["TIME"], las["MT"], "TEMPER")

    MEM_FILES = (MF_RSD, MF_RLD, MF_RLD_ON_RSD, MF_MT)

    ###### for check find_temperature_rise_point_right
    # print(find_temperature_rise_point_right(las["MT"], 1))


    # find_temperature_drop_point вычисляет точку в которой функция температуры начинает идти вниз
    T_max_index, T_max = find_temperature_drop_point(las["MT"], 2)
    if not T_max_index:
        print('program not defined boundaries beetwen heating and cooling')
        print('may be temperature function only show heating')
        plot_part = 2


    # print(T_max_index)

    # choice: 1 - for heating, 2 - for cooling
    # print(las["MT"][:T_max_index])

    (heating_table, cooling_table) = get_calc_for_tables(
        plot_part,
        window_size,
        las["MT"],  
        smoothed_RSD, 
        smoothed_RLD, 
        RLD_on_RSD
        )

    conclusion = get_conclusion(heating_table, cooling_table)
    

    params = (
        serial_number, 
        date, 
        instrument_name, 
        heating_table, 
        cooling_table, 
        conclusion, 
        las["MT"][0], 
        las["MT"].max(),
        las["MT"][-1], 
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
