from geopandas import GeoDataFrame
import pandas as pd
from shapely.geometry import MultiLineString,Polygon
from pyvista import PolyData
from networkx import Graph
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter

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

    def __init__(self, gdf: GeoDataFrame = None):
        self._df = None
        self._vtk_obj = None
        self._network_obj = None
        if gdf is not None:
            self.entity_df = gdf

    @abstractmethod
    def process_df(self):
        pass

    @abstractmethod
    def process_vtk(self):
        pass
    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        self._df = gdf
        self.process_df()

    @property
    def vtk_object(self):

        if self._vtk_obj is None:
            obj = Rep.vtk_rep(self.entity_df)
            return obj
        else:
            return self._vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: PolyData):
        self._vtk_obj = obj
        self.process_vtk()

    @property
    def network_object(self):

        obj = Rep.networkx_rep(self.vtk_object)
        return obj

    @network_object.setter
    def network_object(self, obj: Graph):
        self._network_obj = obj


class Nodes(BaseEntity):

    def process_df(self):

        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'node'

    def process_vtk(self):
        pass

class Fractures(BaseEntity):

    def process_df(self):

        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'fracture'

    def process_vtk(self):
        pass


class Boundary(BaseEntity):

    def process_df(self):
        df = self.entity_df

        geom_list = []
        # boundaries = df.boundary
        #
        # gdf = boundaries.explode(ignore_index=True)

        # The following is horrible and I hate it but for some reason the commented lines above
        # do not work for shapely 1.8 and geopandas 0.11 while they work perfectly with 2.0 and 0.13

        # This is to suppress the SettingWithCopyWarning (we are not working on a copy)
        pd.options.mode.chained_assignment = None

        for index, line in enumerate(df.loc[:, 'geometry']):
            if isinstance(line, Polygon):
                bound = line.boundary
                if isinstance(bound, MultiLineString):
                    for linestring in bound.geoms:
                        geom_list.append(linestring)
                else:
                    geom_list.append(bound)
            else:
                geom_list.append(line)

        for index, value in enumerate(geom_list):
            df.loc[index, 'geometry'] = value

        # When PZero moves to shapely 2.0 remove the lines between the comments
        # and uncomment the two lines above

        if 'type' not in df.columns:
            df['type'] = 'boundary'

    def process_vtk(self):
        pass


class FractureNetwork(BaseEntity):

    def __init__(self, gdf: GeoDataFrame = None):

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

    def process_vtk(self):
        frac_net_vtk = self.vtk_object
        frac_vtk = frac_net_vtk.extract_points(frac_net_vtk.point_data['type'] == 'fracture', include_cells=True)
        bound_vtk = frac_net_vtk.extract_points(frac_net_vtk.point_data['type'] == 'boundary', include_cells=True)

        geometry_filter = vtkGeometryFilter()
        geometry_filter.SetInputData(frac_vtk)
        geometry_filter.Update()
        self.fractures.vtk_object = PolyData(geometry_filter.GetOutput())
        geometry_filter.SetInputData(bound_vtk)
        geometry_filter.Modified()
        geometry_filter.Update()
        self.boundaries.vtk_object = PolyData(geometry_filter.GetOutput())

        # node_vtk = frac_net.extract_points(frac_net.point_data['type'] == 'nodes', include_cells=True)

    def add_fractures(self, fractures: Fractures):

        if self.entity_df is None:
            df = fractures.entity_df
        else:
            df = GeoDataFrame(
                    pd.concat(
                        [self.entity_df, fractures.entity_df[['type', 'geometry']]],
                        ignore_index=True)
            )

        self.fractures = fractures
        self.entity_df = df

    def add_boundaries(self, boundaries: Boundary):

        if self.entity_df is None:
            df = boundaries.entity_df
        else:
            df = GeoDataFrame(
                pd.concat(
                    [self.entity_df,
                     boundaries.entity_df[['type', 'geometry']]],
                    ignore_index=True)
            )
        self.boundaries = boundaries
        self.entity_df = df

    def add_nodes(self, nodes: Nodes):

        if self.entity_df is None:
            df = nodes.entity_df
        else:
            df = GeoDataFrame(
                pd.concat(
                    [self.entity_df,
                     nodes.entity_df[['type', 'geometry']]],
                    ignore_index=True)
            )
        self.boundaries = nodes
        self.entity_df = df
