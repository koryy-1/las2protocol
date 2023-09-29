from abc import ABC, abstractmethod

class AbstractColumnData(ABC):
    @property
    @abstractmethod
    def near_probe(self):
        pass

    @property
    @abstractmethod
    def far_probe(self):
        pass

    @property
    @abstractmethod
    def temper(self):
        pass

    @property
    @abstractmethod
    def default_temper(self):
        pass

    @property
    @abstractmethod
    def near_probe_threshold(self):
        pass

    @property
    @abstractmethod
    def far_probe_threshold(self):
        pass


class ColumnDataGamma(AbstractColumnData):
    _near_probe = 'RSD'
    _far_probe = 'RLD'
    _temper = 'T_GGKP'
    _default_temper = 'MT'
    _near_probe_threshold = 'THLDS'
    _far_probe_threshold = 'THLDL'

    @property
    def near_probe(self):
        return self._near_probe

    @property
    def far_probe(self):
        return self._far_probe

    @property
    def temper(self):
        return self._temper

    @property
    def default_temper(self):
        return self._default_temper

    @property
    def near_probe_threshold(self):
        return self._near_probe_threshold

    @property
    def far_probe_threshold(self):
        return self._far_probe_threshold


class ColumnDataNeutronic(AbstractColumnData):
    _near_probe = 'NTNC'
    _far_probe = 'FTNC'
    # _temper = 'T_NNKT'
    _temper = 'T_GGKP'
    _default_temper = 'MT'
    _near_probe_threshold = ''
    _far_probe_threshold = ''

    @property
    def near_probe(self):
        return self._near_probe

    @property
    def far_probe(self):
        return self._far_probe

    @property
    def temper(self):
        return self._temper

    @property
    def default_temper(self):
        return self._default_temper

    @property
    def near_probe_threshold(self):
        return self._near_probe_threshold

    @property
    def far_probe_threshold(self):
        return self._far_probe_threshold