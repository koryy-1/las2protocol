import numpy as np
import pandas as pd

def calculate_metrics(
        choice: int,
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
    RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, T_base = initialize_base_values(choice, WINDOW_SIZE, TEMPER, RSD, RLD, RLD_on_RSD)

    # Вычисление максимальных и минимальных значений с учетом базовых
    RSD_MAX, RLD_MAX, RLD_ON_RSD_MAX, RSD_MIN, RLD_MIN, RLD_ON_RSD_MIN = calculate_extremum_values(RSD, RLD, RLD_on_RSD, RSD_BASE, RLD_BASE, RLD_ON_RSD_BASE, TEMPER)
    
    # RSD (RLD) +- 0.5% это для отличия флуктуации от максимума и минимума

    RSD_MAX = (RSD.max(), TEMPER[RSD.argmax()]) if is_extremum_point(RSD_BASE, RSD.max(), 0.005) else (RSD_BASE, T_base)
    RLD_MAX = (RLD.max(), TEMPER[RLD.argmax()]) if is_extremum_point(RLD_BASE, RLD.max(), 0.005) else (RLD_BASE, T_base)
    RLD_ON_RSD_MAX = (RLD_on_RSD.max(), TEMPER[RLD_on_RSD.argmax()]) if is_extremum_point(RLD_ON_RSD_BASE, RLD_on_RSD.max(), 0.005) else (RLD_ON_RSD_BASE, T_base)

    RSD_MIN = (RSD.min(), TEMPER[RSD.argmin()]) if is_extremum_point(RSD_BASE, RSD.min(), 0.005) else (RSD_BASE, T_base)
    RLD_MIN = (RLD.min(), TEMPER[RLD.argmin()]) if is_extremum_point(RLD_BASE, RLD.min(), 0.005) else (RLD_BASE, T_base)
    RLD_ON_RSD_MIN = (RLD_on_RSD.min(), TEMPER[RLD_on_RSD.argmin()]) if is_extremum_point(RLD_ON_RSD_BASE, RLD_on_RSD.min(), 0.005) else (RLD_ON_RSD_BASE, T_base)

    RSD_MAX_DIFF = RSD_MAX[0] - RSD_BASE
    RLD_MAX_DIFF = RLD_MAX[0] - RLD_BASE
    RLD_ON_RSD_MAX_DIFF = RLD_ON_RSD_MAX[0] - RLD_ON_RSD_BASE

    RSD_MIN_DIFF = RSD_BASE - RSD_MIN[0]
    RLD_MIN_DIFF = RLD_BASE - RLD_MIN[0]
    RLD_ON_RSD_MIN_DIFF = RLD_ON_RSD_BASE - RLD_ON_RSD_MIN[0]

    RSD_PERCENT_MAX = RSD_MAX_DIFF / RSD_BASE
    RLD_PERCENT_MAX = RLD_MAX_DIFF / RLD_BASE
    RLD_ON_RSD_PERCENT_MAX = RLD_ON_RSD_MAX_DIFF / RLD_ON_RSD_BASE

    RSD_PERCENT_MIN = RSD_MIN_DIFF / RSD_BASE
    RLD_PERCENT_MIN = RLD_MIN_DIFF / RLD_BASE
    RLD_ON_RSD_PERCENT_MIN = RLD_ON_RSD_MIN_DIFF / RLD_ON_RSD_BASE
    
    # print(RSD_BASE, np.round(RSD_BASE))
    # print(RLD_BASE, np.round(RLD_BASE))
    # print(RLD_ON_RSD_BASE, np.round(RLD_ON_RSD_BASE))
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
            interval_for_base_value = min((len(TEMPER) - 1) - T_base_max_index, WINDOW_SIZE * 5)
            RSD_BASE = np.average(RSD[(len(RSD) - 1) - interval_for_base_value:])
            RLD_BASE = np.average(RLD[(len(RLD) - 1) - interval_for_base_value:])
            RLD_ON_RSD_BASE = np.average(RLD_on_RSD[(len(RLD_on_RSD) - 1) - interval_for_base_value:])

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

def exceeds_threshold(calculation_table):
    max_percent_diff = max(
        abs(calculation_table[5][2]), abs(calculation_table[5][3]), abs(calculation_table[5][4]),
        abs(calculation_table[6][2]), abs(calculation_table[6][3]), abs(calculation_table[6][4])
    )
    return max_percent_diff >= 5
    
def find_temperature_drop_point(temp_data, tolerance_degrees):
    T_max_index = np.argmax(temp_data)
    T_max = temp_data[T_max_index]
    T_max_index_last = T_max_index
    for i in range(T_max_index, len(temp_data)):
        # Вычисляем разницу между максимальным и текущим значением
        temp_difference = T_max - temp_data[i]
        if T_max == temp_data[i]:
            T_max_index_last = i
        
        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом уменьшения
        if temp_difference >= tolerance_degrees:
            return T_max_index_last, temp_data[T_max_index_last]  # Возвращаем индекс и значение температуры
    return None  # Если уменьшения не обнаружено

def find_temperature_rise_point(temp_data, tolerance_degrees):
    for i in range(0, len(temp_data) - 1):
        # Вычисляем разницу между следующим и текущим значением
        temp_difference = temp_data[i + 1] - temp_data[i]
        
        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом увеличения
        if temp_difference >= tolerance_degrees:
            return i, temp_data[i]  # Возвращаем индекс и значение температуры
    print('program not defined start of heating')
    return None  # Если увеличения не обнаружено

def find_temperature_rise_point_right(temp_data, tolerance_degrees):
    for i in range(len(temp_data) - 1, 0, -1):
        # Вычисляем разницу между текущим и следующим значением
        temp_difference = temp_data[i - 1] - temp_data[i]

        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом увеличения
        if temp_difference >= tolerance_degrees:
            return i, temp_data[i]  # Возвращаем индекс и значение температуры
    print('program not defined start of heating in right side of temp plot')
    return None  # Если увеличения не обнаружено справа

def is_extremum_point(base, extremum_point, threshold):
    """
    сравнивает отклонение экстремума от базового значения с пороговым значением.
    """
    return abs(base - extremum_point) / base > threshold

def find_min_variance_interval(data, interval_length=60):
    min_variance = float('inf')  # Начальное значение минимальной дисперсии
    min_variance_interval = []  # Инициализация интервала с минимальной дисперсией
    min_variance_index = 0  # Индекс начала интервала с минимальной дисперсией

    for i in range(0, len(data) - interval_length + 1, interval_length):
        interval = data[i:i + interval_length]  # Выбираем интервал длиной 60 отсчетов
        variance = np.var(interval)  # Вычисляем дисперсию интервала

        # Если текущая дисперсия меньше минимальной, обновляем значения
        if variance < min_variance:
            min_variance = variance
            min_variance_interval = interval
            min_variance_index = i

    return min_variance_interval, min_variance, min_variance_index

def moving_average(data, window_size, count):
    smoothed_data = data
    for _ in range(count):
        smoothed_data = pd.Series(smoothed_data).rolling(window=window_size).mean().iloc[window_size-1:].values
    return smoothed_data