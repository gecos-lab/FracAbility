import geopandas
import pandas as pd
import shapely.geometry as geom
from vtkmodules.all import *
import numpy as np
import pyvista as pv

from fracability.Representations import Representation

from abc import ABC, abstractmethod


class BaseEntity(ABC):

    """
    Abstract class for Fracture network entities:

    1. Nodes
    2. Fractures
    3. Boundaries
    4. Fracture Networks
    """

    def __init__(self, gdf: geopandas.GeoDataFrame = None):
        """
        All entities can have as input a gdf or be empty. For example a FractureNetwork
        can be instantiated directly if a gdf contains the distinction between fractures and
        boundaries.
        The dataframe is saved in old_df
        :param gdf: Geopandas Dataframe
        """

        self.df = gdf
        self.old_df = None
        self.process_df()
        self.save_copy()

    @abstractmethod
    def process_df(self):
        """
        All entities modify the input gdf in different ways
        :return: Returns a processed geopandas dataframe
        """
        pass

    @property
    def entity_df(self):
        return self.df

    def get_output(self, entity_repr: Representation):
        """
        Get the output in the desired representation format (for example VTK)
        :param entity_repr: Representation class
        :return: The output depends on the passed representation class
        """
        output = entity_repr.get_repr()
        return output

    def center_object(self, trans_center: np.array = None):
        """
        Center the network. If the translation point is not
        given then the centroid of the network will coincide with the world origin.
        :param trans_center: Point to translate to
        :return:
        """
        self.save_copy() # create a backup copy
        if trans_center is None:
            trans_center = np.array(self.df.dissolve().centroid[0].coords).flatten()

        self.df['geometry'] = self.df.translate(-trans_center[0], -trans_center[1])

    def save_copy(self):
        """
        Save a copy of the self.df in self.old_df
        """
        self.old_df = self.df.copy()


class Nodes(BaseEntity):
    """
    Nodes class defines the nodes of a given fracture network
    """

    def process_df(self):
        ...


class Fractures(BaseEntity):

    """
    Fracture class defines the fractures (both as a single set or a combination of sets)
    of a given fracture network.

    """

    def process_df(self):
        if 'type' not in self.df.columns:
            self.df['type'] = 'fracture'

        if 'U-nodes' not in self.df.columns:
            self.df['U-nodes'] = 0
        self.save_copy()


class Boundary(BaseEntity):

    def process_df(self):

        boundaries = self.df.boundary  # boundaries must be provided as polygons

        self.df['geometry'] = boundaries

        n = self.df.shape[0]
        for i, geometry in enumerate(boundaries):
            if isinstance(geometry, geom.MultiLineString):
                self.df.drop(index=i, inplace=True)

                for line in geometry.geoms:
                    self.df.loc[n, 'geometry'] = line
                    n += 1
                # print(bound_df)
        if 'type' not in self.df.columns:
            self.df['type'] = 'boundary'

        if 'U-nodes' not in self.df.columns:
            self.df['U-nodes'] = 0
        self.save_copy()


class FractureNetwork(BaseEntity):
    """
    The FractureNetwork class is the combination of the BaseEntities
    (Nodes, Fractures, Boundary)
    """
    def __init__(self):
        super().__init__()
        self.fractures: Fractures = None
        self.boundaries: Boundary = None
        self.nodes: Nodes = None

    def process_df(self):
        if self.df is None:
            self.df = geopandas.GeoDataFrame(pd.DataFrame(
                {'type': [], 'U-nodes': [], 'geometry': []}))

    def add_fractures(self, fractures: Fractures):
        """
        Function used to add a Fracture object to the dataset. The created dataframe is also saved
        in old_df for safe keeping

        :param fractures: Fractures object
        :return:
        """
        self.fractures = fractures
        self.df = geopandas.GeoDataFrame(pd.concat([self.df,
                                                    self.fractures.entity_df[
                                                        ['geometry', 'type', 'U-nodes']]],
                                                   ignore_index=True))
        self.old_df = self.df.copy()

    def add_boundaries(self, boundaries: Boundary):
        """
        Function used to add a Boundary object to the dataset. The created dataframe is also saved
        in old_df for safe keeping
        :param boundaries: Boundaries object
        :return:
        """
        self.boundaries = boundaries
        self.df = geopandas.GeoDataFrame(pd.concat([self.df,
                                                    self.boundaries.entity_df[
                                                        ['geometry', 'type', 'U-nodes']]],
                                                   ignore_index=True))
        self.old_df = self.df.copy()
