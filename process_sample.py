import numpy as np
import win32com.client
import datetime

from calculations import *

from calc_types import TemperatureType, ParametersForReporting

from docx_creator import make_docx

from plot_creator import create_graph

# main
def get_calc_for_tables(
        is_heating: bool,
        is_cooling: bool,
        window_size: int,
        T_max_index: int,
        TEMPER: np.ndarray,  
        smoothed_near_probe: np.ndarray, 
        smoothed_far_probe: np.ndarray, 
        far_on_near_probe: np.ndarray
        ):
    heating_table = None
    cooling_table = None
    if is_heating:
        heating_table = calculate_metrics(
            TemperatureType.HEATING, 
            window_size, 
            TEMPER[:T_max_index], 
            smoothed_near_probe[:T_max_index], 
            smoothed_far_probe[:T_max_index], 
            far_on_near_probe[:T_max_index]
            )

    # для охлада базовая темп = последний минимум
    # print(las["MT"][T_max_index:])
    if is_cooling:
        cooling_table = calculate_metrics(
            TemperatureType.COOLING, 
            window_size, 
            TEMPER[T_max_index:], 
            smoothed_near_probe[T_max_index:], 
            smoothed_far_probe[T_max_index:], 
            far_on_near_probe[T_max_index:]
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
    
def is_doc_open():
    try:
        word_app = win32com.client.GetActiveObject("Word.Application")
        return bool(word_app.ActiveDocument)
    except:
        return False
    
def close_active_docx_wnd(doc_name):
    if is_doc_open():
        word_app = win32com.client.GetActiveObject("Word.Application")
        for doc in word_app.Documents:
            if doc.Name == doc_name:
                doc.Close()
                break

def save2doc(window_size, is_heating, is_cooling, description, data, titles, thresholds):
    serial_number, date, instrument_name = description

    (NEAR_PROBE, FAR_PROBE, FAR_ON_NEAR_PROBE), TEMPER, TIME = data

    near_probe_title, far_probe_title = titles

    THLDS, THLDL = thresholds

    ### creating graphs #######################
    # print('creating graphs...')
    MF_NEAR_PROBE = create_graph(TIME, NEAR_PROBE, f"{near_probe_title}_1")
    MF_FAR_PROBE = create_graph(TIME, FAR_PROBE, f"{far_probe_title}_1")
    MF_FAR_ON_NEAR_PROBE = create_graph(TIME, FAR_ON_NEAR_PROBE, f"{far_probe_title}/{near_probe_title}")
    MF_MT = create_graph(TIME, TEMPER, "TEMPER")

    MEM_FILES = (MF_NEAR_PROBE, MF_FAR_PROBE, MF_FAR_ON_NEAR_PROBE, MF_MT)

    # for check find_temperature_rise_point_right
    # print(find_temperature_rise_point_right(TEMPER, 1))


    ### find point when temper drop down #######################
    # todo: отработать случай когда график темпы только падает
    # find_temperature_drop_point вычисляет точку в которой функция температуры начинает идти вниз
    T_max_index, _ = find_temperature_drop_point(TEMPER, 2)
    if not T_max_index:
        print('program not defined boundaries beetwen heating and cooling')
        print('may be temperature function only show heating')
        is_cooling = False
    # print(T_max_index)

    # print(TEMPER[:T_max_index])


    ### get calculations #######################
    (heating_table, cooling_table) = get_calc_for_tables(
        is_heating,
        is_cooling,
        window_size,
        T_max_index,
        TEMPER,  
        NEAR_PROBE, 
        FAR_PROBE, 
        FAR_ON_NEAR_PROBE
        )


    ### get conclusion #######################
    conclusion = get_conclusion(heating_table, cooling_table)
    

    ### create and save .docx file #######################
    params_for_reporting = ParametersForReporting()
    params_for_reporting.serial_number = serial_number
    params_for_reporting.date = date
    params_for_reporting.instrument_name = instrument_name
    params_for_reporting.heating_table = heating_table
    params_for_reporting.cooling_table = cooling_table
    params_for_reporting.conclusion = conclusion
    params_for_reporting.temp_min_left = TEMPER[:T_max_index].min()
    params_for_reporting.temp_max = TEMPER.max()
    params_for_reporting.temp_min_right = TEMPER[T_max_index:].min()
    params_for_reporting.near_probe_title = near_probe_title
    params_for_reporting.far_probe_title = far_probe_title
    params_for_reporting.near_probe_threshold = THLDS
    params_for_reporting.far_probe_threshold = THLDL


    current_date = datetime.datetime.now().strftime('%d%m%y')
    output_filename = f"{serial_number}_{instrument_name}_{current_date}_by_program"
    # print(f'creating {output_filename}.docx...')
    doc = make_docx(params_for_reporting, MEM_FILES, picture_size=6.5)

    close_active_docx_wnd(f'{output_filename}.docx')

    try:
        doc.save(f'{output_filename}.docx')
        return True
        # print('docx successfully saved')
        # print('Done.')
    except:
        return False
        # print()
        # print(f'ERROR: failed to save {output_filename}.docx')
