import geopandas
import pandas as pd
import shapely.geometry as geom
from vtkmodules.all import *
import numpy as np
import pyvista as pv

import fracability.Representations as Rep

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
        self.vtk_obj = None
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

    def get_vtk_output(self):
        """
        Get the output in the desired representation format (for example VTK)
        :param entity_repr: Representation class
        :return: The output depends on the passed representation class
        """
        self.vtk_obj = Rep.vtk_rep(self.entity_df)
        return self.vtk_obj

    def get_network_output(self):
        """
        Get the output in the desired representation format (for example VTK)
        :param entity_repr: Representation class
        :return: The output depends on the passed representation class
        """
        output = Rep.networkx_rep(self.get_vtk_output())
        return output

    def center_object(self, trans_center: np.array = None, return_center = False):
        """
        Center the network. If the translation point is not
        given then the centroid of the network will coincide with the world origin.
        :param trans_center: Point to translate to
        :param return_center: Flag to enable the return of the translation center
        :return:
        """
        self.save_copy() # create a backup copy
        if trans_center is None:
            trans_center = np.array(self.df.dissolve().centroid[0].coords).flatten()

        self.df['geometry'] = self.df.translate(-trans_center[0], -trans_center[1])
        if return_center:
            return trans_center

    def save_copy(self):
        """
        Save a copy of the self.df in self.old_df
        """
        self.old_df = self.df.copy()

    def get_nodes(self) -> pv.PolyData:
        points = pv.PolyData(self.get_vtk_output().points)
        return points

class Nodes(BaseEntity):
    """
    Nodes class defines the nodes of a given fracture network
    """

    ...


class Fractures(BaseEntity):

    """
    Fracture class defines the fractures (both as a single set or a combination of sets)
    of a given fracture network.

    """

    def process_df(self):
        if 'type' not in self.df.columns:
            self.df['type'] = 'fracture'

        self.save_copy()


class Boundary(BaseEntity):

    def process_df(self):

        for index, boundary in enumerate(self.df['geometry']):
            if isinstance(boundary, geom.Polygon):
                self.df.loc[index, 'geometry'] = boundary.boundary
        self.df = self.df.explode()
        # n = self.df.shape[0]
        # for i, geometry in enumerate(self.df):
        #     if isinstance(geometry, geom.MultiLineString):
        #         self.df.drop(index=i, inplace=True)
        #
        #         for line in geometry.geoms:
        #             self.df.loc[n, 'geometry'] = line
        #             n += 1
                # print(bound_df)
        if 'type' not in self.df.columns:
            self.df['type'] = 'boundary'

        self.save_copy()


class FractureNetwork(BaseEntity):
    """
    The FractureNetwork class is the combination of the BaseEntities
    (Nodes, Fractures, Boundary)
    """
    def __init__(self, gdf: geopandas.GeoDataFrame=None):
        super().__init__(gdf)
        self.fractures: Fractures = None
        self.boundaries: Boundary = None
        self.nodes: Nodes = None
        self.process_df()
        self.save_copy()

    def process_df(self):
        if self.df is None:
            self.df = geopandas.GeoDataFrame(pd.DataFrame(
                {'type': [], 'geometry': []}))
        else:
            # print(self.df)
            self.save_copy()
            fractures = Fractures(self.df.loc[self.df['type'] == 'fracture'])
            boundary = Boundary(self.df.loc[self.df['type'] == 'boundary'])
            # nodes = Nodes(self.df.loc[self.df['type'] == 'nodes'])

            self.fractures = fractures
            self.boundaries = boundary

            # self.nodes = nodes

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
                                                        ['geometry', 'type']]],
                                                   ignore_index=True))
        self.save_copy()

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
                                                        ['geometry', 'type']]],
                                                   ignore_index=True))
        self.save_copy()



