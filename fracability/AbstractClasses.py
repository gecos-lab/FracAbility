from abc import ABC, abstractmethod, abstractproperty

from geopandas import GeoDataFrame
from geopandas import read_file
from pyvista import PolyData
from networkx import Graph
import scipy.stats as ss
import numpy as np
from copy import deepcopy


class BaseEntity(ABC):
    """
    Abstract class for Fracture network entities:

    1. Nodes
    2. Fractures
    3. Boundaries
    4. Fracture Networks
    """

    def __init__(self, gdf: GeoDataFrame = None, shp: str = None):
        """
        Init the entity. If a geopandas dataframe is specified then it is
        set as the source entity df.

        :param gdf: Geopandas dataframe
        """
        self._df: GeoDataFrame = GeoDataFrame()

        if shp is not None:
            self.entity_df = read_file(shp)
        elif gdf is not None:
            self.entity_df = gdf

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
    def matplot(self):
        """
        Plot entity using matplotlib backend
        :return:
        """

    @abstractmethod
    def vtkplot(self):
        """
        Plot entity using vtk backend
        :return:
        """

    @property
    def name(self) -> str:
        """
        Property used to return the name of the class (i.e. Fractures)
        :return: Name of the class as string
        """
        return self.__class__.__name__

    @property
    def crs(self) -> str:
        """
        Property used to return the crs of the entity
        :return: Name of the coordinate system as a string
        """
        return self.entity_df.crs

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

    def save_csv(self, path: str, sep: str = ',', index: bool = False):
        """
        Save the entity df as csv
        :param index:
        :type sep: object
        :param path:
        :return:
        """

        self.entity_df.to_csv(path, sep=sep, index=index)

    def save_shp(self, path: str):
        """
        Save the entity df as shp
        :param path:
        :return:
        """
        if not self.entity_df.empty:
            self.entity_df.to_file(path, crs=self.crs)


class BaseOperator(ABC):
    """
    Abstract class for Operators such as:

    1. Geometry operations
    2. Topology operations
    3. Statistics operations

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
