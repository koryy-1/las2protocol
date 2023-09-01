import numpy as np

def get_calculation_table(
        TEMPER: np.ndarray,  
        RSD: np.ndarray, 
        RLD: np.ndarray, 
        RLD_on_RSD: np.ndarray):
    
    T_base = TEMPER.min()
    
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
        (6, '% MAX',                np.round(RSD_PERCENT_MAX, 3) * 100,  np.round(RLD_PERCENT_MAX, 3) * 100, np.round(RLD_ON_RSD_PERCENT_MAX, 3) * 100),
        (7, '% MIN',                np.round(RSD_PERCENT_MIN, 3) * 100,  np.round(RLD_PERCENT_MIN, 3) * 100, np.round(RLD_ON_RSD_PERCENT_MIN, 3) * 100)
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