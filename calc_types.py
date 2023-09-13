from enum import Enum
from typing import Any, Literal

class TemperatureType(Enum):
    HEATING = 1
    COOLING = 2

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
    RSD_threshold: float
    RLD_threshold: float