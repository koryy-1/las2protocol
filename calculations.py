import numpy as np
import pandas as pd
import sys

def get_calculation_table(
        choice: int,
        WINDOW_SIZE: int,
        TEMPER: np.ndarray,  
        RSD: np.ndarray, 
        RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray):
    
    RSD_BASE = 0
    RLD_BASE = 0
    RLD_ON_RSD_BASE = 0
    T_base = 0

    # choice: 1 - for heating, 2 - for cooling
    if choice == 1:
        # взять первые или последние 3-5 интервалов по 4 минуты или до первого изменения нач темпы и вычислить среднее значение
        # получится значение RSD базовой по базовой темп
        T_base_max_index, T_base = find_temperature_rise_point(TEMPER, 1)
        
        # print('T_base_max_index', T_base_max_index, T_base)
        index_for_base_value = 0
        if T_base_max_index < WINDOW_SIZE * 5:
            index_for_base_value = T_base_max_index
        else:
            index_for_base_value = WINDOW_SIZE * 5

        # после нахождения базовой температуры находим RSD_base RLD_base RLD_on_RSD_base
        # print('for RSD_BASE', RSD[:index_for_base_value])
        RSD_BASE = np.average(RSD[:index_for_base_value])
        RLD_BASE = np.average(RLD[:index_for_base_value])
        RLD_ON_RSD_BASE = np.average(RLD_on_RSD[:index_for_base_value])
    elif choice == 2:
        # взять первые или последние 3-5 интервалов по 4 минуты или до первого изменения нач темпы и вычислить среднее значение
        # получится значение RSD базовой по базовой темп
        T_base_max_index, T_base = find_temperature_rise_point_right(TEMPER, 1)
        # print('T_base_max_index', T_base_max_index, T_base)
        index_for_base_value = 0
        if (len(TEMPER) - 1) - T_base_max_index < WINDOW_SIZE * 5:
            index_for_base_value = T_base_max_index
        else:
            index_for_base_value = WINDOW_SIZE * 5

        # после нахождения базовой температуры находим RSD_base RLD_base RLD_on_RSD_base
        # print('for RSD_BASE', RSD[index_for_base_value:])
        RSD_BASE = np.average(RSD[index_for_base_value:])
        RLD_BASE = np.average(RLD[index_for_base_value:])
        RLD_ON_RSD_BASE = np.average(RLD_on_RSD[index_for_base_value:])
    
    # RSD (RLD) +- 0.5% это для отличия флуктуации от максимума и минимума

    RSD_MAX = (RSD.max(), TEMPER[RSD.argmax()]) if is_extremum_point(RSD_BASE, RSD.max(), 0.005) else (RSD_BASE, T_base)
    RLD_MAX = (RLD.max(), TEMPER[RLD.argmax()]) if is_extremum_point(RLD_BASE, RLD.max(), 0.005) else (RLD_BASE, T_base)
    RLD_ON_RSD_MAX = (RLD_on_RSD.max(), TEMPER[RLD_on_RSD.argmax()]) if is_extremum_point(RLD_ON_RSD_BASE, RLD_on_RSD.max(), 0.005) else (RLD_ON_RSD_BASE, T_base)

    RSD_MIN = (RSD.min(), TEMPER[RSD.argmin()]) if is_extremum_point(RSD_BASE, RSD.min(), 0.005) else (RSD_BASE, T_base)
    RLD_MIN = (RLD.min(), TEMPER[RLD.argmin()]) if is_extremum_point(RLD_BASE, RLD.min(), 0.005) else (RLD_BASE, T_base)
    RLD_ON_RSD_MIN = (RLD_on_RSD.min(), TEMPER[RLD_on_RSD.argmin()]) if is_extremum_point(RLD_ON_RSD_BASE, RLD_on_RSD.min(), 0.005) else (RLD_ON_RSD_BASE, T_base)

    RSD_MAX_BASE = RSD_MAX[0] - RSD_BASE
    RLD_MAX_BASE = RLD_MAX[0] - RLD_BASE
    RLD_ON_RSD_MAX_BASE = RLD_ON_RSD_MAX[0] - RLD_ON_RSD_BASE

    RSD_BASE_MIN = RSD_BASE - RSD_MIN[0]
    RLD_BASE_MIN = RLD_BASE - RLD_MIN[0]
    RLD_ON_RSD_BASE_MIN = RLD_ON_RSD_BASE - RLD_ON_RSD_MIN[0]

    RSD_PERCENT_MAX = RSD_MAX_BASE / RSD_BASE
    RLD_PERCENT_MAX = RLD_MAX_BASE / RLD_BASE
    RLD_ON_RSD_PERCENT_MAX = RLD_ON_RSD_MAX_BASE / RLD_ON_RSD_BASE

    RSD_PERCENT_MIN = RSD_BASE_MIN / RSD_BASE
    RLD_PERCENT_MIN = RLD_BASE_MIN / RLD_BASE
    RLD_ON_RSD_PERCENT_MIN = RLD_ON_RSD_BASE_MIN / RLD_ON_RSD_BASE
    
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

def exceeds_threshold(calculation_table):
    if (abs(calculation_table[5][2]) < 5 and
        abs(calculation_table[5][3]) < 5 and
        abs(calculation_table[5][4]) < 5 and
        abs(calculation_table[6][2]) < 5 and
        abs(calculation_table[6][3]) < 5 and
        abs(calculation_table[6][4]) < 5):
        return False
    else:
        return True
    
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
    print('exit from program')
    sys.exit()
    # return None  # Если увеличения не обнаружено

def find_temperature_rise_point_right(temp_data, tolerance_degrees):
    for i in range(len(temp_data) - 1, 0, -1):
        # Вычисляем разницу между текущим и следующим значением
        temp_difference = temp_data[i - 1] - temp_data[i]

        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом увеличения
        if temp_difference >= tolerance_degrees:
            return i, temp_data[i]  # Возвращаем индекс и значение температуры
    print('program not defined start of heating in right side of temp plot')
    print('exit from program')
    sys.exit()
    # return None  # Если увеличения не обнаружено справа

def is_extremum_point(base, extremum_point, threshold):
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