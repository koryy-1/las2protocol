import numpy as np
from utils import *
from models.TempType import TempType


def calculate_metrics(
        temper_type: int,
        WINDOW_SIZE: int,
        TEMPER: np.ndarray,  
        RSD: np.ndarray, 
        RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray):
    
    """
    Вычисляет метрики и создает таблицу.

    Args:
        choice (int): Выбор: 1 - для нагрева, 2 - для охлаждения.
        TEMPER (np.ndarray): Массив с данными о температуре.
        WINDOW_SIZE (int): Размер окна для вычислений.
        RSD (np.ndarray): Данные RSD.
        RLD (np.ndarray): Данные RLD.
        RLD_on_RSD (np.ndarray): Данные RLD_on_RSD.

    Returns:
        tuple: Таблица с метриками.
    """
    
    # Инициализация базовых значений
    RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base = initialize_base_values(
        temper_type, WINDOW_SIZE, TEMPER, RSD, RLD, RLD_on_RSD
    )

    # Вычисление максимальных и минимальных значений с учетом базовых
    (RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, 
     RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN) = calculate_extremum_values(
        RSD, RLD, RLD_on_RSD, RSD_BASE, 
        RLD_BASE, RLD_ON_RSD_BASE, TEMPER, T_base
    )

    # Вычисление разниц между максимальными и минимальными значениями и их базовыми значениями
    (RSD_MAX_DIFF, RLD_MAX_DIFF, RLD_ON_RSD_MAX_DIFF, 
     RSD_MIN_DIFF, RLD_MIN_DIFF, RLD_ON_RSD_MIN_DIFF) = calculate_value_differences(
        RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, 
        RLD_ON_RSD_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE
    )

    # Вычисление процентных изменений
    (RSD_PERCENT_MAX, RLD_PERCENT_MAX, RLD_ON_RSD_PERCENT_MAX, 
     RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN) = calculate_percent_differences(
        RSD_MAX_DIFF, RLD_MAX_DIFF, RLD_ON_RSD_MAX_DIFF, RSD_MIN_DIFF, 
        RLD_MIN_DIFF, RLD_ON_RSD_MIN_DIFF, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE
    )

    # Создание и возврат таблицы с метриками
    calculation_table = create_calculation_table(
        T_base, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX,
        RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_MAX_DIFF, RLD_MAX_DIFF, RLD_ON_RSD_MAX_DIFF,
        RSD_MIN_DIFF, RLD_MIN_DIFF, RLD_ON_RSD_MIN_DIFF, RSD_PERCENT_MAX, RLD_PERCENT_MAX,
        RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN
    )

    return calculation_table

def initialize_base_values(temper_type, WINDOW_SIZE, TEMPER, RSD, RLD, RLD_on_RSD):
    RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base = 0, 0, 0, 0

    if temper_type == TempType.HEATING:
        T_base_max_index, T_base = find_temperature_rise_point(TEMPER, 1)
        if T_base_max_index:
            index_for_base_value = min(T_base_max_index, WINDOW_SIZE * 5)
            RSD_BASE = np.average(RSD[:index_for_base_value])
            RLD_BASE = np.average(RLD[:index_for_base_value])
            RLD_ON_RSD_BASE = np.average(RLD_on_RSD[:index_for_base_value])
    elif temper_type == TempType.COOLING:
        T_base_max_index, T_base = find_temperature_rise_point_right(TEMPER, 1)
        if T_base_max_index:
            if ((len(TEMPER) - 1) - T_base_max_index < WINDOW_SIZE * 5):
                index_for_base_value = T_base_max_index
            else:
                index_for_base_value = (len(TEMPER) - 1) - WINDOW_SIZE * 5

            RSD_BASE = np.average(RSD[index_for_base_value:])
            RLD_BASE = np.average(RLD[index_for_base_value:])
            RLD_ON_RSD_BASE = np.average(RLD_on_RSD[index_for_base_value:])

    return RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base

def calculate_extremum_values(RSD, RLD, RLD_on_RSD, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, TEMPER, T_base):
    RSD_MAX = calculate_extremum(RSD, TEMPER, RSD_BASE, T_base)
    RLD_MAX = calculate_extremum(RLD, TEMPER, RLD_BASE, T_base)
    RLD_ON_RSD_MAX = calculate_extremum(RLD_on_RSD, TEMPER, RLD_ON_RSD_BASE, T_base)

    RSD_MIN = calculate_extremum(RSD, TEMPER, RSD_BASE, T_base, is_max=False)
    RLD_MIN = calculate_extremum(RLD, TEMPER, RLD_BASE, T_base, is_max=False)
    RLD_ON_RSD_MIN = calculate_extremum(RLD_on_RSD, TEMPER, RLD_ON_RSD_BASE, T_base, is_max=False)

    return RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN

def calculate_extremum_values_with_indexes(RSD, RLD, RLD_on_RSD, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, TEMPER, T_base):
    RSD_MAX = calculate_extremum_with_indexes(RSD, TEMPER, RSD_BASE, T_base)
    RLD_MAX = calculate_extremum_with_indexes(RLD, TEMPER, RLD_BASE, T_base)
    RLD_ON_RSD_MAX = calculate_extremum_with_indexes(RLD_on_RSD, TEMPER, RLD_ON_RSD_BASE, T_base)

    RSD_MIN = calculate_extremum_with_indexes(RSD, TEMPER, RSD_BASE, T_base, is_max=False)
    RLD_MIN = calculate_extremum_with_indexes(RLD, TEMPER, RLD_BASE, T_base, is_max=False)
    RLD_ON_RSD_MIN = calculate_extremum_with_indexes(RLD_on_RSD, TEMPER, RLD_ON_RSD_BASE, T_base, is_max=False)

    return RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN

def get_interval_near_extremum(data, extremum_index):
    return data[extremum_index - int(0.01 * len(data)):extremum_index + int(0.01 * len(data))]

def calculate_extremum(data, TEMPER, base, T_base, is_max=True):
    extremum_value = data.max() if is_max else data.min()
    extremum_index = data.argmax() if is_max else data.argmin()
    extremum_temperature = TEMPER[extremum_index]

    interval_near_extremum = get_interval_near_extremum(data, extremum_index)
    extremum_value = np.average(interval_near_extremum)

    # RSD (RLD) +- 0.5% это для отличия флуктуации от максимума и минимума
    return (extremum_value, extremum_temperature) if is_extremum_point(base, extremum_value, 0.005) else (base, T_base)

def calculate_extremum_with_indexes(data, TEMPER, base, T_base, is_max=True):
    extremum_value = data.max() if is_max else data.min()
    extremum_index = data.argmax() if is_max else data.argmin()
    extremum_temperature = TEMPER[extremum_index]

    interval_near_extremum = get_interval_near_extremum(data, extremum_index)
    extremum_value = np.average(interval_near_extremum)

    # RSD (RLD) +- 0.5% это для отличия флуктуации от максимума и минимума
    return (extremum_index, extremum_value) if is_extremum_point(base, extremum_value, 0.005) else (base, T_base)

def calculate_value_differences(RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE):
    RSD_MAX_DIFF = RSD_MAX[0] - RSD_BASE
    RLD_MAX_DIFF = RLD_MAX[0] - RLD_BASE
    RLD_ON_RSD_MAX_DIFF = RLD_ON_RSD_MAX[0] - RLD_ON_RSD_BASE

    RSD_MIN_DIFF = RSD_MIN[0] - RSD_BASE
    RLD_MIN_DIFF = RLD_MIN[0] - RLD_BASE
    RLD_ON_RSD_MIN_DIFF = RLD_ON_RSD_MIN[0] - RLD_ON_RSD_BASE

    return RSD_MAX_DIFF, RLD_MAX_DIFF, RLD_ON_RSD_MAX_DIFF, RSD_MIN_DIFF, RLD_MIN_DIFF, RLD_ON_RSD_MIN_DIFF

def calculate_percent_differences(RSD_MAX_BASE, RLD_MAX_BASE, RLD_ON_RSD_MAX_BASE, RSD_BASE_MIN, RLD_BASE_MIN, RLD_ON_RSD_BASE_MIN, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE):
    RSD_PERCENT_MAX = RSD_MAX_BASE / RSD_BASE
    RLD_PERCENT_MAX = RLD_MAX_BASE / RLD_BASE
    RLD_ON_RSD_PERCENT_MAX = RLD_ON_RSD_MAX_BASE / RLD_ON_RSD_BASE

    RSD_PERCENT_MIN = RSD_BASE_MIN / RSD_BASE
    RLD_PERCENT_MIN = RLD_BASE_MIN / RLD_BASE
    RLD_ON_RSD_PERCENT_MIN = RLD_ON_RSD_BASE_MIN / RLD_ON_RSD_BASE

    return RSD_PERCENT_MAX, RLD_PERCENT_MAX, RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN

def create_calculation_table(T_base, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX,
                            RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN, RSD_MAX_DIFF, RLD_MAX_DIFF, RLD_ON_RSD_MAX_DIFF,
                            RSD_MIN_DIFF, RLD_MIN_DIFF, RLD_ON_RSD_MIN_DIFF, RSD_PERCENT_MAX, RLD_PERCENT_MAX,
                            RLD_ON_RSD_PERCENT_MAX, RSD_PERCENT_MIN, RLD_PERCENT_MIN, RLD_ON_RSD_PERCENT_MIN):
    calculation_table = (
        (1, f'N(T={int(T_base)})',       int(np.round(RSD_BASE)),         int(np.round(RLD_BASE)),        np.round(RLD_ON_RSD_BASE, 3)),
        (2, 'MAX/T',                f'{int(np.round(RSD_MAX[0]))}({RSD_MAX[1]})',        f'{int(np.round(RLD_MAX[0]))}({RLD_MAX[1]})',       f'{np.round(RLD_ON_RSD_MAX[0], 3)}({RLD_ON_RSD_MAX[1]})'),
        (3, 'MIN/T',                f'{int(np.round(RSD_MIN[0]))}({RSD_MIN[1]})',        f'{int(np.round(RLD_MIN[0]))}({RLD_MIN[1]})',       f'{np.round(RLD_ON_RSD_MIN[0], 3)}({RLD_ON_RSD_MIN[1]})'),
        (4, f'MAX - N(T={int(T_base)})', int(np.round(RSD_MAX_DIFF)),     int(np.round(RLD_MAX_DIFF)),    np.round(RLD_ON_RSD_MAX_DIFF, 3)),
        (5, f'N(T={int(T_base)}) - MIN', int(np.round(RSD_MIN_DIFF)),     int(np.round(RLD_MIN_DIFF)),    np.round(RLD_ON_RSD_MIN_DIFF, 3)),
        (6, '% MAX',                np.round(RSD_PERCENT_MAX * 100, 2),  np.round(RLD_PERCENT_MAX * 100, 2), np.round(RLD_ON_RSD_PERCENT_MAX * 100, 2)),
        (7, '% MIN',                np.round(RSD_PERCENT_MIN * 100, 2),  np.round(RLD_PERCENT_MIN * 100, 2), np.round(RLD_ON_RSD_PERCENT_MIN * 100, 2))
    )
    return calculation_table

def is_extremum_point(base, extremum_point, threshold):
    """
    сравнивает отклонение экстремума от базового значения с пороговым значением.
    """
    return abs(base - extremum_point) / base > threshold
