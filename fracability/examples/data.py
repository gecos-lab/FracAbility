"""
Module used to import the example data from the Pontrelli quarry.
"""

from fracability.AbstractClasses import AbstractReadDataClass
from os.path import dirname, join


class Pontrelli(AbstractReadDataClass):
    def __init__(self):
        super().__init__()
        self.path = join(dirname(__file__), 'datasets', 'cava_pontrelli')


class Salza(AbstractReadDataClass):
    def __init__(self):
        super().__init__()
        self.path = join(dirname(__file__), 'datasets', 'laghetto_salza')

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


