from reliability import Fitters, Distributions, Reliability_testing
from abc import ABC, abstractmethod
from fracability.Entities import BaseEntity

class AbstractStatistics(ABC)

    def __init__(self,obj: BaseEntity = None):
        self._obj: BaseEntity = obj
        self._lengths: list = []
        self._censored_lengths: list = []

        if obj is not None:
            self._data_adapter()

    @property
    def lengths(self):
        return self._lengths

    @lengths.setter
    def lengths(self,length_list: list = []):
        self._lengths = length_list
    def _data_adapter(self):

        entity_df = self._obj.entity_df
        self._lengths = entity_df.loc[entity_df['censoring'] == 0, 'length']
        self._censored_lengths = entity_df.loc[entity_df['censoring'] == 1, 'length']