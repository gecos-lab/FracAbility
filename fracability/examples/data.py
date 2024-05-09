"""
Module used to import the example data from the Pontrelli quarry.
"""

from abc import ABC, abstractmethod, abstractproperty
from os.path import dirname, join, basename
import glob


class AbstractReadDataClass(ABC):
    """
    :param extension: String of extension to search in the dataset directory. Default is .shp
    """
    def __init__(self, extension='.shp'):
        self._path: str = ''
        self.extension = extension
        pass

    @property
    def path(self) -> str:
        """
        Set or get the path of the dataset
        """

        return self._path

    @path.setter
    def path(self, path: str):
        self._path = path

    @property
    def data_dict(self) -> dict:
        """
        Return a dict of name: path of the available data for the given dataset
        :param extension: String of extension to search in the dataset directory. Default is .shp
        :return:
        """

        paths = glob.glob(join(self.path, f'*{self.extension}'))

        file_names = [basename(path) for path in paths]

        data_dict = {file_name: path for file_name, path in zip(file_names, paths)}

        return data_dict

    @property
    def available_data(self) -> list:
        """
        Return a list of names of the available data for the given dataset
        :return:
        """

        return list(self.data_dict.keys())

    @property
    def available_paths(self) -> list:
        """
        Return a list of names of the available data for the given dataset
        :return:
        """

        return list(self.data_dict.values())


class Pontrelli(AbstractReadDataClass):
    def __init__(self):
        super().__init__()
        self.path = join(dirname(__file__), 'datasets', 'cava_pontrelli')


class Salza(AbstractReadDataClass):
    def __init__(self):
        super().__init__()
        self.path = join(dirname(__file__), 'datasets', 'laghetto_salza')


class QgisStyle(AbstractReadDataClass):
    def __init__(self):
        super().__init__(extension='.qml')
        self.path = join(dirname(__file__), 'datasets', 'qgis_styles')

#
#
#
# def get_Pontrelli_data_paths() -> dict:
#     """
#     Function used to get the different data as absolute paths in dictionary form for the Pontrelli dataset
#     :return: Dictionary of absolute paths for the given dataset
#     """
#     file_path = dirname(__file__)
#
#     path_dict = {'Boundary': join(file_path, 'datasets', 'cava_pontrelli', 'Interpretation_boundary.shp'),
#                  'Set a': join(file_path, 'datasets', 'cava_pontrelli', 'Set_a.shp'),
#                  'Set b': join(file_path, 'datasets', 'cava_pontrelli', 'Set_b.shp'),
#                  'Set c': join(file_path, 'datasets', 'cava_pontrelli', 'Set_c.shp')}
#
#     return path_dict
#
#
# def get_Salza_data_paths() -> dict:
#     """
#     Function used to get the different data as absolute paths in dictionary form the Laghetto Salza dataset
#     :return: Dictionary of absolute paths for the given dataset
#     """
#     file_path = dirname(__file__)
#
#     path_dict = {'Boundary': join(file_path, 'datasets', 'laghetto_salza', 'Interpretation_boundary.shp'),
#                  'Set 1': join(file_path, 'datasets', 'laghetto_salza', 'Set_1.shp'),
#                  'Set 2': join(file_path, 'datasets', 'laghetto_salza', 'Set_2.shp')}
#
#     return path_dict


