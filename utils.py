import numpy as np

from calculations import *

def calculate_metrics(
        choice: int,
        WINDOW_SIZE: int,
        TEMPER: np.ndarray,  
        RSD: np.ndarray, 
        RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray):
    
    # Инициализация базовых значений
    RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base = initialize_base_values(choice, WINDOW_SIZE, TEMPER, RSD, RLD, RLD_on_RSD)

    # Вычисление максимальных и минимальных значений с учетом базовых
    RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN = calculate_extremum_values(RSD, RLD, RLD_on_RSD, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, TEMPER)

    # Вычисление разниц между максимальными и минимальными значениями и процентных изменений
    RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE, RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN = calculate_value_differences(RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE)

    # Вычисление процентных изменений
    RSD_PERCENT_MAX, RLD_PERCENT_MAX, RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN = calculate_percent_differences(RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE, RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE)

    # Создание и возврат таблицы с метриками
    calculation_table = create_calculation_table(T_base, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX,
                                                RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE,
                                                RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN, RSD_PERCENT_MAX, RLD_PERCENT_MAX,
                                                RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN)
    
    return calculation_table

def initialize_base_values(choice, WINDOW_SIZE, TEMPER, RSD, RLD, RLD_on_RSD):
    RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base = 0, 0, 0, 0

    if choice == 1:
        T_base_max_index, T_base = find_temperature_rise_point(TEMPER, 1)
        if T_base_max_index:
            index_for_base_value = min(T_base_max_index, WINDOW_SIZE * 5)
            RSD_BASE = np.average(RSD[:index_for_base_value])
            RLD_BASE = np.average(RLD[:index_for_base_value])
            RLD_ON_RSD_BASE = np.average(RLD_on_RSD[:index_for_base_value])
    elif choice == 2:
        T_base_max_index, T_base = find_temperature_rise_point_right(TEMPER, 1)
        if T_base_max_index:
            index_for_base_value = min((len(TEMPER) - 1) - T_base_max_index, WINDOW_SIZE * 5)
            RSD_BASE = np.average(RSD[(len(RSD) - 1) - ((len(TEMPER) - 1) - index_for_base_value):])
            RLD_BASE = np.average(RLD[(len(RLD) - 1) - ((len(TEMPER) - 1) - index_for_base_value):])
            RLD_ON_RSD_BASE = np.average(RLD_on_RSD[(len(RLD_on_RSD) - 1) - ((len(TEMPER) - 1) - index_for_base_value):])

    return RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base

def calculate_extremum_values(RSD, RLD, RLD_on_RSD, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, TEMPER):
    RSD_MAX = calculate_extremum(RSD, RSD_BASE, TEMPER)
    RLD_MAX = calculate_extremum(RLD, RLD_BASE, TEMPER)
    RLD_ON_RSD_MAX = calculate_extremum(RLD_on_RSD, RLD_ON_RSD_BASE, TEMPER)

    RSD_MIN = calculate_extremum(RSD, RSD_BASE, TEMPER, is_max=False)
    RLD_MIN = calculate_extremum(RLD, RLD_BASE, TEMPER, is_max=False)
    RLD_ON_RSD_MIN = calculate_extremum(RLD_on_RSD, RLD_ON_RSD_BASE, TEMPER, is_max=False)

    return RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN

def calculate_extremum(data, base, TEMPER, is_max=True):
    extremum_value = data.max() if is_max else data.min()
    extremum_index = data.argmax() if is_max else data.argmin()
    extremum_temperature = TEMPER[extremum_index]
    return (extremum_value, extremum_temperature) if is_extremum_point(base, extremum_value, 0.005) else (base, TEMPER[extremum_index])

def calculate_value_differences(RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE):
    RSD_MAX_BASE = RSD_MAX[0] - RSD_BASE
    RLD_MAX_BASE = RLD_MAX[0] - RLD_BASE
    RLD_ON_RSD_MAX_BASE = RLD_ON_RSD_MAX[0] - RLD_ON_RSD_BASE

    RSD_BASE_MIN = RSD_BASE - RSD_MIN[0]
    RLD_BASE_MIN = RLD_BASE - RLD_MIN[0]
    RLD_ON_RSD_BASE_MIN = RLD_ON_RSD_BASE - RLD_ON_RSD_MIN[0]

    return RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE, RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN

def calculate_percent_differences(RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE, RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE):
    RSD_PERCENT_MAX = RSD_MAX_BASE / RSD_BASE
    RLD_PERCENT_MAX = RLD_MAX_BASE / RLD_BASE
    RLD_ON_RSD_PERCENT_MAX = RLD_ON_RSD_MAX_BASE / RLD_ON_RSD_BASE

    RSD_PERCENT_MIN = RSD_BASE_MIN / RSD_BASE
    RLD_PERCENT_MIN = RLD_BASE_MIN / RLD_BASE
    RLD_ON_RSD_PERCENT_MIN = RLD_ON_RSD_BASE_MIN / RLD_ON_RSD_BASE

    return RSD_PERCENT_MAX, RLD_PERCENT_MAX, RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN

def create_calculation_table(T_base, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX,
                            RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE,
                            RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN, RSD_PERCENT_MAX, RLD_PERCENT_MAX,
                            RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN):
    calculation_table = (
        (1, f'N(T={int(T_base)})',       int(np.round(RSD_BASE)),         int(np.round(RLD_BASE)),        np.round(RLD_ON_RSD_BASE, 3)),
        (2, 'MAX/T',                f'{int(np.round(RSD_MAX[0]))}({RSD_MAX[1]})',        f'{int(np.round(RLD_MAX[0]))}({RLD_MAX[1]})',       f'{np.round(RLD_ON_RSD_MAX[0], 3)}({RLD_ON_RSD_MAX[1]})'),
        (3, 'MIN/T',                f'{int(np.round(RSD_MIN[0]))}({RSD_MIN[1]})',        f'{int(np.round(RLD_MIN[0]))}({RLD_MIN[1]})',       f'{np.round(RLD_ON_RSD_MIN[0], 3)}({RLD_ON_RSD_MIN[1]})'),
        (4, f'MAX - N(T={int(T_base)})', int(np.round(RSD_MAX_BASE)),     int(np.round(RLD_MAX_BASE)),    np.round(RLD_ON_RSD_MAX_BASE, 3)),
        (5, f'N(T={int(T_base)}) - MIN', int(np.round(RSD_BASE_MIN)),     int(np.round(RLD_BASE_MIN)),    np.round(RLD_ON_RSD_BASE_MIN, 3)),
        (6, '% MAX',                np.round(RSD_PERCENT_MAX * 100, 2),  np.round(RLD_PERCENT_MAX * 100, 2), np.round(RLD_ON_RSD_PERCENT_MAX * 100, 2)),
        (7, '% MIN',                np.round(RSD_PERCENT_MIN * 100, 2),  np.round(RLD_PERCENT_MIN * 100, 2), np.round(RLD_ON_RSD_PERCENT_MIN * 100, 2))
    )
    return calculation_table
