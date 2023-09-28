from typing import Any, Literal, Tuple

class ParamsForReport():
    def __init__(
        self,
        serial_number: str,
        date: str,
        instrument_name: str,
        heating_table: Tuple[Tuple[Literal[1], str, int, int, Any], ...] | None,
        cooling_table: Tuple[Tuple[Literal[1], str, int, int, Any], ...] | None,
        conclusion: str,
        temp_min_left: float,
        temp_max: float,
        temp_min_right: float,
        near_probe_title: str,
        far_probe_title: str,
        near_probe_threshold: float,
        far_probe_threshold: float
    ):
        self.serial_number = serial_number
        self.date = date
        self.instrument_name = instrument_name
        self.heating_table = heating_table
        self.cooling_table = cooling_table
        self.conclusion = conclusion
        self.temp_min_left = temp_min_left
        self.temp_max = temp_max
        self.temp_min_right = temp_min_right
        self.near_probe_title = near_probe_title
        self.far_probe_title = far_probe_title
        self.near_probe_threshold = near_probe_threshold
        self.far_probe_threshold = far_probe_threshold