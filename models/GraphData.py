import numpy as np

class GraphData():
    near_probe: np.ndarray = []
    far_probe: np.ndarray = []
    far_on_near_probe: np.ndarray = []
    temper: np.ndarray = []
    time: np.ndarray = []
    near_probe_threshold: str
    far_probe_threshold: str

