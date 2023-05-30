import geopandas
import pandas as pd
import shapely.geometry as geom
from vtkmodules.all import *
import numpy as np
import pyvista as pv
from networkx import Graph

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
        self._df = None
        self._vtk_obj = None
        self._network_obj = None
        if gdf is not None:
            self._df = gdf
            self.process_df()

    @abstractmethod
    def process_df(self):
        """
        All entities modify the input gdf in different ways
        :return: Returns a processed geopandas dataframe
        """
        pass

    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: geopandas.GeoDataFrame):
        self._df = gdf

    @property
    def vtk_object(self):
        """
        Get the output in the desired representation format (for example VTK)
        :param entity_repr: Representation class
        :return: The output depends on the passed representation class
        """
        if self._vtk_obj is None:
            obj = Rep.vtk_rep(self.entity_df)
            return obj
        else:
            return self._vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: pv.PolyData):
        self._vtk_obj = obj

    @property
    def network_object(self):
        """
        Get the output in the desired representation format (for example VTK)
        :param entity_repr: Representation class
        :return: The output depends on the passed representation class
        """
        obj = Rep.networkx_rep(self.vtk_object)
        return obj

    @network_object.setter
    def network_object(self, obj: Graph):
        self._network_obj = obj

    # def get_nodes(self) -> pv.PolyData:
    #     if self.
    #     obj = self.vtk_object
    #     points = pv.PolyData(obj.points)
    #
    #     for arr in obj.array_names:
    #         if len(obj[arr]) == obj.n_points:
    #             points[arr] = obj[arr]
    #     return points


class Nodes(BaseEntity):
    """
    Nodes class defines the nodes of a given fracture network
    """

    def process_df(self):

        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'node'

        self.entity_df = df


class Fractures(BaseEntity):

    """
    Fracture class defines the fractures (both as a single set or a combination of sets)
    of a given fracture network.

    """

    def process_df(self):

        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'fracture'

        self.entity_df = df


class Boundary(BaseEntity):

    def process_df(self):
        df = self.entity_df
        crs = df.crs
        gdf = geopandas.GeoDataFrame({'geometry': []}, crs=crs)
        for index, line in enumerate(df['geometry']):
            if isinstance(line, geom.Polygon):
                gdf.loc[index, 'geometry'] = line.boundary
            else:
                gdf.loc[index, 'geometry'] = line

        df = gdf.explode(ignore_index=True)

        if 'type' not in df.columns:
            df['type'] = 'boundary'

        self.entity_df = df


class FractureNetwork(BaseEntity):
    """
    The FractureNetwork class is the combination of the BaseEntities
    (Nodes, Fractures, Boundary)
    """
    def __init__(self, gdf: geopandas.GeoDataFrame = None):

        self._fractures: Fractures = None
        self._boundaries: Boundary = None
        self._nodes: Nodes = None

        super().__init__(gdf)

    @property
    def fractures(self) -> Fractures:
        return self._fractures

    @fractures.setter
    def fractures(self, frac_obj: Fractures):
        self._fractures = frac_obj

    @property
    def boundaries(self) -> Boundary:
        return self._boundaries

    @boundaries.setter
    def boundaries(self, bound_obj: Boundary):
        self._boundaries = bound_obj

    @property
    def nodes(self) -> Nodes:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes_obj: Nodes):
        self._nodes = nodes_obj

    def process_df(self):
        df = self.entity_df
        fractures = Fractures(df.loc[df['type'] == 'fracture'])
        boundary = Boundary(df.loc[df['type'] == 'boundary'])
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

        if self.entity_df is None:
            df = fractures.entity_df
        else:
            df = geopandas.GeoDataFrame(
                    pd.concat(
                        [self.entity_df, fractures.entity_df[['type', 'geometry']]],
                        ignore_index=True)
            )

        self.fractures = fractures
        self.entity_df = df

    def add_boundaries(self, boundaries: Boundary):
        """
        Function used to add a Boundary object to the dataset. The created dataframe is also saved
        in old_df for safe keeping
        :param boundaries: Boundaries object
        :return:
        """

        if self.entity_df is None:
            df = boundaries.entity_df
        else:
            df = geopandas.GeoDataFrame(
                pd.concat(
                    [self.entity_df,
                     boundaries.entity_df[['type', 'geometry']]],
                    ignore_index=True)
            )
        self.boundaries = boundaries
        self.entity_df = df

    def add_nodes(self, nodes: Nodes):
        """
        Function used to add a Boundary object to the dataset. The created dataframe is also saved
        in old_df for safe keeping
        :param boundaries: Boundaries object
        :return:
        """

        if self.entity_df is None:
            df = nodes.entity_df
        else:
            df = geopandas.GeoDataFrame(
                pd.concat(
                    [self.entity_df,
                     nodes.entity_df[['type', 'geometry']]],
                    ignore_index=True)
            )
        self.boundaries = nodes
        self.entity_df = df


