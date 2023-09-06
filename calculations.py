import numpy as np

def get_calculation_table(
        WINDOW_SIZE: int,
        TEMPER: np.ndarray,  
        RSD: np.ndarray, 
        RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray):
    
    # взять первые 3-5 интервалов или до первого изменения нач темпы по 4 минуты и вычислить среднее значение
    # получится значение RSD базовой по базовой темп
    T_base = np.amin(TEMPER[:WINDOW_SIZE * 5])
    T_base = np.average(TEMPER[:WINDOW_SIZE * 5])
    T_base = find_temperature_rise_point(TEMPER, 1)
    print('T_base', T_base)

    # RSD (RLD) +- 0.5% это для отличия флуктуации от максимума и минимума

    # после нахождения базовой темпы находим RSD.min() RLD.min() RLD_on_RSD.min() 

    # проделать вычисления для охлада

    # для охлада базовая темп = последний минимум

    print(find_temperature_drop_point(TEMPER, 3))




    
    RSD_BASE = RSD[TEMPER.argmax()]
    RLD_BASE = RLD[TEMPER.argmax()]
    RLD_ON_RSD_BASE = RLD_on_RSD[TEMPER.argmax()]
    
    # RSD_MAX_T = f'{RSD.max()}({TEMPER[RSD.argmax()]})'
    # RLD_MAX_T = f'{RLD.max()}({TEMPER[RLD.argmax()]})'
    # RLD_ON_RSD_MAX_T = f'{RLD_on_RSD.max()}({TEMPER[RLD_on_RSD.argmax()]})'
    RSD_MAX_T = RSD.max()
    RLD_MAX_T = RLD.max()
    RLD_ON_RSD_MAX_T = RLD_on_RSD.max()

    # RSD_MIN_T = f'{RSD.min()}({TEMPER[RSD.argmin()]})'
    # RLD_MIN_T = f'{RLD.min()}({TEMPER[RLD.argmin()]})'
    # RLD_ON_RSD_MIN_T = f'{RLD_on_RSD.min()}({TEMPER[RLD_on_RSD.argmin()]})'
    RSD_MIN_T = RSD.min()
    RLD_MIN_T = RLD.min()
    RLD_ON_RSD_MIN_T = RLD_on_RSD.min()

    RSD_MAX_BASE = RSD_MAX_T - RSD_BASE
    RLD_MAX_BASE = RLD_MAX_T - RLD_BASE
    RLD_ON_RSD_MAX_BASE = RLD_ON_RSD_MAX_T - RLD_ON_RSD_BASE

    RSD_BASE_MIN = RSD_BASE - RSD_MIN_T
    RLD_BASE_MIN = RLD_BASE - RLD_MIN_T
    RLD_ON_RSD_BASE_MIN = RLD_ON_RSD_BASE - RLD_ON_RSD_MIN_T

    RSD_PERCENT_MAX = RSD_MAX_BASE / RSD_BASE
    RLD_PERCENT_MAX = RLD_MAX_BASE / RLD_BASE
    RLD_ON_RSD_PERCENT_MAX = RLD_ON_RSD_MAX_BASE / RLD_ON_RSD_BASE

    RSD_PERCENT_MIN = RSD_BASE_MIN / RSD_BASE
    RLD_PERCENT_MIN = RLD_BASE_MIN / RLD_BASE
    RLD_ON_RSD_PERCENT_MIN = RLD_ON_RSD_BASE_MIN / RLD_ON_RSD_BASE
    
    calculation_table = (
        (1, f'N(T={T_base})',       np.round(RSD_BASE),         np.round(RLD_BASE),        np.round(RLD_ON_RSD_BASE, 3)),
        (2, 'MAX/T',                np.round(RSD_MAX_T),        np.round(RLD_MAX_T),       np.round(RLD_ON_RSD_MAX_T, 3)),
        (3, 'MIN/T',                np.round(RSD_MIN_T),        np.round(RLD_MIN_T),       np.round(RLD_ON_RSD_MIN_T, 3)),
        (4, f'MAX - N(T={T_base})', np.round(RSD_MAX_BASE),     np.round(RLD_MAX_BASE),    np.round(RLD_ON_RSD_MAX_BASE, 3)),
        (5, f'N(T={T_base}) - MIN', np.round(RSD_BASE_MIN),     np.round(RLD_BASE_MIN),    np.round(RLD_ON_RSD_BASE_MIN, 3)),
        (6, '% MAX',                np.round(RSD_PERCENT_MAX * 100, 3),  np.round(RLD_PERCENT_MAX * 100, 3), np.round(RLD_ON_RSD_PERCENT_MAX * 100, 3)),
        (7, '% MIN',                np.round(RSD_PERCENT_MIN * 100, 3),  np.round(RLD_PERCENT_MIN * 100, 3), np.round(RLD_ON_RSD_PERCENT_MIN * 100, 3))
    )

    return calculation_table

def get_conclusion(calculation_table):
    # todo: math.abs
    if (abs(calculation_table[5][2]) < 5 and
        abs(calculation_table[5][3]) < 5 and
        abs(calculation_table[5][4]) < 5 and
        abs(calculation_table[6][2]) < 5 and
        abs(calculation_table[6][3]) < 5 and
        abs(calculation_table[6][4]) < 5):
        return 'не превышает'
    else:
        return 'превышает'
    
def find_temperature_drop_point(temp_data, tolerance_degrees):
    T_max_index = np.argmax(temp_data)
    T_max = temp_data[T_max_index]
    for i in range(T_max_index, len(temp_data)):
        # Вычисляем разницу между текущим и предыдущим значением
        temp_difference = T_max - temp_data[i]
        
        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом уменьшения
        if temp_difference >= tolerance_degrees:
            return i, temp_data[i]  # Возвращаем индекс и значение температуры
    return None  # Если уменьшения не обнаружено

def find_temperature_rise_point(temp_data, tolerance_degrees):
    for i in range(1, len(temp_data)):
        # Вычисляем разницу между текущим и предыдущим значением
        temp_difference = temp_data[i] - temp_data[i - 1]
        
        # Если разница превышает заданный порог (tolerance_degrees), это может быть началом увеличения
        if temp_difference >= tolerance_degrees:
            return i, temp_data[i]  # Возвращаем индекс и значение температуры
    return None  # Если увеличения не обнаружено