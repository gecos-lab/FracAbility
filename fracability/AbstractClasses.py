import os.path
import shutil
from abc import ABC, abstractmethod, abstractproperty
from fracability.examples.data import QgisStyle


from geopandas import GeoDataFrame
from geopandas import read_file
from pyvista import PolyData
from networkx import Graph
import scipy.stats as ss
import numpy as np
from copy import deepcopy
from shapely import remove_repeated_points


class BaseEntity(ABC):
    """
    Abstract class for Fracture network entities:

    1. Nodes
    2. Fractures
    3. Boundaries
    4. Fracture Networks
    """

    def __init__(self, gdf: GeoDataFrame = None, csv: str = None, shp: str = None):
        """
        Init the entity. If a geopandas dataframe is specified then it is
        set as the source entity df.

        Parameters
        -----------
        gdf: GeoDataFrame
            Use as input a geopandas dataframe
        csv: str
            Use as input a csv indicated by the path
        shp: str
            Use as input a shapefile indicated by the path

        Notes
        --------
        The csv needs to have a "geometry" column. If missing the import will fail.
        """

        self._df: GeoDataFrame = GeoDataFrame()
        if gdf is not None:
            self.entity_df = gdf
        elif csv is not None:
            gdf = read_file(csv, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")
            if 'geometry' not in self.entity_df.columns:
                exit('Missing geometry column, terminating')
            else:
                self.entity_df = gdf
        elif shp is not None:
            self.entity_df = read_file(shp)

    @property
    def name(self) -> str:
        """
        Property used to return the name of the current class as a string.
        """
        return self.__class__.__name__

    @property
    @abstractmethod
    def entity_df(self) -> GeoDataFrame:
        """
        Each entity is based on a geopandas dataframe. This property returns or sets
        the entity_df of the given entity.

        :getter: Returns the GeoDataFrame
        :setter: Sets the GeoDataFrame
        :type: GeoDataFrame

        Notes
        -------
        When set, the dataframe is modified to conform to the assigned entity structure.
        """

        pass

    @entity_df.setter
    def entity_df(self, gpd: GeoDataFrame = None):
        self._df = gpd

    @property
    @abstractmethod
    def vtk_object(self) -> PolyData:
        """
        Each entity can be represented with a vtk object.
        This returns a Pyvista PolyData object representing the entity_df.

        :getter: Returns a Pyvista PolyData object
        :setter: Sets a generic Pyvista DataSet
        :type: pyvista PolyData

        Notes
        -------
        When the get method is applied the PolyData is build **on the fly** using the entity_df as a source.

        When set the DataSet is **cast to a PolyData**.
        """
        pass

    @property
    @abstractmethod
    def network_object(self) -> Graph:
        """
        Each entity can be represented with a networkx graph.
        This returns the network object using the vtk object (and so the df).

        :getter: Returns a networkx Graph object
        :setter: Sets a Graph object
        :type: pyvista Graph

        Notes
        -------
        When the get method is applied the Graph is build **on the fly** using the object and so the entity_df.
        """

        pass

    @abstractmethod
    def mat_plot(self):
        """
        Plot entity using matplotlib backend
        """

    @abstractmethod
    def vtk_plot(self):
        """
        Plot entity using vtk backend
        """

    @property
    def crs(self) -> str:
        """
        Property used to return the crs of the entity

        :return: Name of the coordinate system as a string
        """
        return self.entity_df.crs

    @crs.setter
    def crs(self, crs):
        """
        Property used to return the crs of the entity

        :return: Name of the coordinate system as a string
        """
        self.entity_df.crs = crs

    @property
    def centroid(self) -> np.ndarray:
        """
        Property used to return the centroid of the entity. Dissolve is used to aggregate each shape in a single entity.

        :return: 1D numpy array of the centroid
        """
        trans_center = np.array(self.entity_df.dissolve().centroid[0].coords).flatten()
        return trans_center

    @property
    def get_copy(self):
        """
        Property used to return a deep copy of the entity

        :return:
        """
        return deepcopy(self)

    def center_object(self, trans_center: np.array = None, return_center: bool = False,
                      inplace: bool = True):
        """
        Method used to center the center of an Entity object to a given point. If no point is specified then the object
        will be moved to the origin (0,0,0).

        Parameters
        ----------
        obj: Boundary, Fractures, FractureNetwork
            A fracability entity object
        trans_center: array
            Point to which translate the object
        return_center: bool
            Bool flag to specify to return the translation center
        inplace: bool
            Bool flag to specify if the operation overwrites the entity or creates a new instance

        Returns
        ----------
        trans_center: array
            Point of translation. If trans_center is not specified in the output then this will return the center of
            the object
        copy_obj: object
            Copy of the modified input object (preserves the original input)
        """

        if self.name == 'FractureNetwork':
            df = self.fracture_network_to_components_df()
        else:
            df = self.entity_df.copy()

        if trans_center is None:
            trans_center = self.centroid

        df['geometry'] = df.translate(-trans_center[0], -trans_center[1])

        if inplace:

            self.entity_df = df

            if return_center:
                return trans_center

        else:
            copy_obj = deepcopy(self)
            copy_obj.entity_df = df

            if return_center:
                return copy_obj, trans_center
            else:
                return copy_obj

    def save_csv(self, path: str, sep: str = ';', index: bool = False):
        """
        Save the entity df as csv

        Parameters
        -------------
        index: Bool
            Indicate whether to include or not the index column
        sep: String
            Indicate the separator string used to save the csv
        path: String
            Indicate the path in where to save the csv. **DO NOT** include the extension (.csv).

        Notes
        ---------

        The csv will be saved in the output/csv directory in the indicated path in the working directory. If this path does not exist, then it will be created.
        """

        if not self.entity_df.empty:
            cwd = os.getcwd()
            output_path = os.path.join(cwd, path, 'output/csv')

            if not os.path.isdir(output_path):
                os.makedirs(output_path)

            if self.name == 'Fractures':
                set_n = list(set(self.entity_df['f_set']))
                for f_set in set_n:
                    final_path = os.path.join(output_path, f'{self.name}_{f_set}.csv')
                    entity_df = self.entity_df.loc[self.entity_df['f_set'] == f_set, :]
                    entity_df.to_csv(final_path, sep=sep, index=index)
            elif self.name == 'Boundary':
                group_n = list(set(self.entity_df['b_group']))
                for b_group in group_n:
                    final_path = os.path.join(output_path, f'{self.name}_{b_group}.csv')
                    entity_df = self.entity_df.loc[self.entity_df['b_group'] == b_group, :]
                    entity_df.to_csv(final_path, sep=sep, index=index)
            else:
                final_path = os.path.join(output_path, f'{self.name}.csv')
                entity_df = self.entity_df
                entity_df.to_csv(final_path, sep=sep, index=index)



        else:
            print('Cannot save an empty entity')

    def save_shp(self, path: str):
        """
        Save the entity df as shapefile

        Parameters
        -------------
        path: String.
            Indicate the path in where to save the csv. **DO NOT** include the extension (.shp).

        Notes
        ---------

        The shapefile will be saved in output/shp directory in the indicated path in the working directory. If this path does not exist, then it will be created.
        """
        if not self.entity_df.empty:
            cwd = os.getcwd()
            output_path = os.path.join(cwd, path, 'output', 'shp')
            style_out = os.path.join(output_path, 'qgis_style')
            if not os.path.isdir(output_path):
                os.makedirs(output_path)
            if not os.path.isdir(style_out):
                os.makedirs(style_out)

            if self.name == 'Fractures' or self.name == 'Backbone':
                set_n = list(set(self.entity_df['f_set']))
                for f_set in set_n:
                    final_path = os.path.join(output_path, f'{self.name}_{f_set}.shp')
                    entity_df = self.entity_df.loc[self.entity_df['f_set'] == f_set, :]
                    entity_df.to_file(final_path, crs=self.crs, engine='fiona')
            elif self.name == 'Boundary':
                group_n = list(set(self.entity_df['b_group']))
                for b_group in group_n:
                    final_path = os.path.join(output_path, f'{self.name}_{b_group}.shp')
                    entity_df = self.entity_df.loc[self.entity_df['b_group'] == b_group, :]
                    entity_df.to_file(final_path, crs=self.crs, engine='fiona')
            elif self.name == 'Nodes':
                final_path = os.path.join(output_path, f'{self.name}.shp')
                entity_df = self.entity_df
                entity_df.to_file(final_path, crs=self.crs, engine='fiona')

            qgis_style_paths = QgisStyle().available_paths

            for qgis_path in qgis_style_paths:
                shutil.copy(qgis_path, style_out)

        else:
            print('Cannot save an empty entity')

    def remove_double_points(self):
        """
        Utility used to clean geometries with double points
        """
        tot_geom = len(self.entity_df.geometry)
        print('\n\n')
        for line, geom in enumerate(self.entity_df.geometry):
            print(f'Removing possible double points on geometries: {line}/{tot_geom}',end='\r')
            self.entity_df.loc[line, 'geometry'] = remove_repeated_points(geom, tolerance=0.000001)


class BaseOperator(ABC):
    """
    Abstract class for Operators such as:

    1. Geometry operations
    2. Topology operations

    This class provides a unified input for the different operators since all are based on the BaseObj and associated
    entity_df
    """

    def __init__(self, obj: BaseEntity):
        self.df = obj.entity_df.loc[obj.entity_df['active_set'] == 1].copy()
        self.obj = obj

    @property
    def name(self):
        return self.__class__.__name__


class AbstractStatistics(ABC):

    def __init__(self, obj: BaseEntity = None):
        self._obj: BaseEntity = obj

        self.data: ss.CensoredData
        self._lengths: np.array

        self._function_list: list = ['pdf', 'cdf', 'sf', 'hf', 'chf']

        if obj is not None:
            self._lengths = obj.entity_df.loc[obj.entity_df['censored'] >= 0, 'length'].values
            entity_df = self._obj.entity_df
            self._complete_lengths = entity_df.loc[entity_df['censored'] == 0, 'length'].values
            self._censored_lengths = entity_df.loc[entity_df['censored'] == 1, 'length'].values

            self.data = ss.CensoredData(uncensored=self._complete_lengths, right=self._censored_lengths)

    @property
    def lengths(self):

        """
        This property returns or sets the complete list of length data for the fracture network

        :getter: Return the complete list of lengths
        :setter: Set the complete list of lengths
        """

        return self._lengths

    @lengths.setter
    def lengths(self, length_list: list = None):
        self._lengths = length_list

    @property
    def complete_lengths(self):

        """
        This property returns or sets the list of non-censored length data of the fracture network

        :getter: Return the list of non-censored data
        :setter: Set the list of non-censored data
        """

        return self.data.__dict__['_uncensored']

    @complete_lengths.setter
    def complete_lengths(self, complete_length_list: list = []):
        self.data = ss.CensoredData(uncensored=complete_length_list, right=self.censored_lengths)

    @property
    def censored_lengths(self):

        """
        This property returns or sets the list of censored length data of the fracture network

        :getter: Return the list of censored data
        :setter: Set the list of censored data
        :return:
        """

        return self.data.__dict__['_right']

    @censored_lengths.setter
    def censored_lengths(self, censored_length_list: list = []):
        self.data = ss.CensoredData(uncensored=self.complete_lengths, right=censored_length_list)

    @property
    def ecdf(self):
        return ss.ecdf(self.data)

    @property
    def function_list(self):
        return self._function_list

