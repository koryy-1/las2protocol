from enum import Enum
from typing import Any, Literal
import numpy as np

class TemperatureType(Enum):
    HEATING = 1
    COOLING = 2

class DeviceType(Enum):
    GAMMA = 1
    NEUTRONIC = 2

class ColumnDataGamma(Enum):
    NEAR_PROBE = 'RSD'
    FAR_PROBE = 'RLD'
    TEMPER = 'T_GGKP'
    DEFAULT_TEMPER = 'MT'
    NEAR_PROBE_THRESHOLD = 'THLDS'
    FAR_PROBE_THRESHOLD = 'THLDL'

class ColumnDataNeutronic(Enum):
    NEAR_PROBE = 'NTNC'
    FAR_PROBE = 'FTNC'
    TEMPER = 'T_NNKT'
    DEFAULT_TEMPER = 'MT'
    # NEAR_PROBE_THRESHOLD = ''
    # FAR_PROBE_THRESHOLD = ''

class GraphData():
    near_probe: np.ndarray = []
    far_probe: np.ndarray = []
    far_on_near_probe: np.ndarray = []
    temper: np.ndarray = []
    time: np.ndarray = []

class ParametersForReporting():
    serial_number: str
    date: str
    instrument_name: str
    heating_table: tuple[tuple[Literal[1], str, int, int, Any], tuple[Literal[2], Literal['MAX/T'], str, str, str], tuple[Literal[3], Literal['MIN/T'], str, str, str], tuple[Literal[4], str, int, int, Any], tuple[Literal[5], str, int, int, Any], tuple[Literal[6], Literal['% MAX'], Any, Any, Any], tuple[Literal[7], Literal['% MIN'], Any, Any, Any]] | None
    cooling_table: tuple[tuple[Literal[1], str, int, int, Any], tuple[Literal[2], Literal['MAX/T'], str, str, str], tuple[Literal[3], Literal['MIN/T'], str, str, str], tuple[Literal[4], str, int, int, Any], tuple[Literal[5], str, int, int, Any], tuple[Literal[6], Literal['% MAX'], Any, Any, Any], tuple[Literal[7], Literal['% MIN'], Any, Any, Any]] | None
    conclusion: str
    temp_min_left: float
    temp_max: float
    temp_min_right: float
    near_probe_title: str
    far_probe_title: str
    near_probe_threshold: float
    far_probe_threshold: float