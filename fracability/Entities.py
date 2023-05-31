from geopandas import GeoDataFrame
import pandas as pd
from shapely.geometry import MultiLineString, Polygon
from pyvista import PolyData, DataSet
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
        """
        Init the entity. If a geopandas dataframe is specified then it is
        set as the source entity df.
        :param gdf: Geopandas dataframe
        """
        self._df = None
        self._vtk_obj = None
        self._network_obj = None
        if gdf is not None:
            self.entity_df = gdf

    @abstractmethod
    def process_df(self):
        """
        Each entity process the input dataframe in different ways
        (for example boundaries vs. fractures).
        Use this method to define the pipeline used to parse the dataframe
        :return:
        """
        pass

    @abstractmethod
    def process_vtk(self):
        """
        Each entity process the vtk objects in different ways (for example frac net vs fractures).
        Use this method to define the pipeline for the vtk objects
        :return:
        """
        pass
    @property
    def entity_df(self) -> GeoDataFrame:
        """
        Each entity is based on a geopandas dataframe. This returns the entity_df.
        :return: A geopandas dataframe
        """
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        Each entity is based on a geopandas dataframe. This method sets and then processes
        the entity_df using the process_df() abstract method.
        :param gdf: The dataframe to set
        """
        self._df = gdf
        self.process_df()

    @property
    def vtk_object(self) -> PolyData:
        """
        Each entity can be represented with a vtk object.
        This returns the object build on the fly using the entity_df.
        :return: A geopandas dataframe
        """
        if self._vtk_obj is None:
            obj = Rep.vtk_rep(self.entity_df)
            return obj
        else:
            return self._vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):
        """
        Each entity can be represented with a vtk object.
        This sets the vtk object forcing it as a vtkPolyData .
        :param obj: vtkDataSet object
        """
        geometry_filter = vtkGeometryFilter()
        geometry_filter.SetInputData(obj)
        geometry_filter.Update()

        self._vtk_obj = PolyData(geometry_filter.GetOutput())
        self.process_vtk()

    @property
    def network_object(self):
        """
        Each entity can be represented with a networkx graph.
        This returns the network object build on the fly
        using the vtk object (and so the df).
        """
        obj = Rep.networkx_rep(self.vtk_object)
        return obj

    @network_object.setter
    def network_object(self, obj: Graph):
        """
        Each entity can be represented with a networkx Graph object.
        This sets the graph object.
        :param obj: Graph object
        """
        self._network_obj = obj


class Nodes(BaseEntity):

    """
    Node base entity, represents all the nodes in the network.
    """

    def process_df(self):
        """
        Each entity process the input dataframe in different ways
        Nodes modify the entity_df only to add the type column (if not
        already present)
        """

        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'node'

    def process_vtk(self):
        pass


class Fractures(BaseEntity):
    """
    Base entity for fractures
    """

    def process_df(self):
        """
        Each entity process the input dataframe in different ways
        Fractures modify the entity_df by adding the 'type' and
        'censored' column (if not already present). The censored column
        is a bool column that identifies if the fracture is censored (1) or
        not (0)
        """
        df = self.entity_df

        if 'type' not in df.columns:
            df['type'] = 'fracture'
        if 'censored' not in df.columns:
            df['censored'] = 0

    def process_vtk(self):
        pass


class Boundary(BaseEntity):
    """
    Base entity for boundaries
    """

    def process_df(self):
        """
        Each entity process the input dataframe in different ways.
        Boundaries modify the entity_df by converting Polygons in Linestrings
        to (using the boundary method) and MultiLinestrings to LineStrings.
        A 'type' column is added if missing.
        """
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

    """
    Fracture network base entity. Fracture networks are defined by one or
    more:

    1. Fracture base entities
    2. Boundary base entities
    3. Nodes base entities

    All the data is represented in the entity_df and the different objects
    are defined by the 'type' column.

    FractureNetwork objects can be created in two ways depending on how
    the dataset is structured.

    1. If fractures and boundaries and nodes are saved in different shp files
    then use the add_fracture,add_boundary and add_nodes methods on an empty
    FractureNetwork object.
    2. If fractures and boundaries and nodes are saved in a single shp the
    geopandas dataframe can be directly fed when instantiating the class.
    In this case a type column must be set to indicate of which type the geometries are

    """

    def __init__(self, gdf: GeoDataFrame = None):

        self._fractures: Fractures = None
        self._boundaries: Boundary = None
        self._nodes: Nodes = None

        # Use the base entity init.
        super().__init__(gdf)

    @property
    def fractures(self) -> Fractures:
        """
        Retrieve the fracture objects
        :return: A fracture object
        """
        return self._fractures

    @fractures.setter
    def fractures(self, frac_obj: Fractures):
        """
        Set the fracture objects
        :param frac_obj: Fracture object to be set
        """
        self._fractures = frac_obj

    @property
    def boundaries(self) -> Boundary:
        """
        Retrieve the Boundary object
        :return: The boundary object
        """
        return self._boundaries

    @boundaries.setter
    def boundaries(self, bound_obj: Boundary):
        """
        Set the boundary objects
        :param bound_obj: Boundary object
        """
        self._boundaries = bound_obj

    @property
    def nodes(self) -> Nodes:
        """
        Retrieve the nodes of the FractureNetwork
        :return: Nodes of the fracture network
        """
        return self._nodes

    @nodes.setter
    def nodes(self, nodes_obj: Nodes):
        """
        Set the nodes of the FractureNetwork
        :param nodes_obj: Nodes to be set
        """
        self._nodes = nodes_obj

    def process_df(self):
        """
        Each entity process the input dataframe in different ways.
        FractureNetworks modify the entity_df by extracting the different types
        (fractures, boundaries, nodes). After that, the appropriate base entities
        are created and set.
        """
        df = self.entity_df
        fractures = Fractures(df.loc[df['type'] == 'fracture'])
        boundary = Boundary(df.loc[df['type'] == 'boundary'])
        # nodes = Nodes(df.loc[df['type'] == 'nodes'])
        self.fractures = fractures
        self.boundaries = boundary
        # self.nodes = nodes

    def process_vtk(self):
        """
        Each entity processes an input vtkobject in different ways.
        FractureNetworks modify the vtkobject by extracting the different types
        (fractures, boundaries, nodes). After that, the appropriate vtkobject is
        set to the corresponding entity
        :return:
        """
        frac_net_vtk = self.vtk_object
        frac_vtk = frac_net_vtk.extract_points(frac_net_vtk.point_data['type'] == 'fracture', include_cells=True,adjacent_cells=False)
        bound_vtk = frac_net_vtk.extract_points(frac_net_vtk.point_data['type'] == 'boundary', include_cells=True,adjacent_cells=False)

        self.fractures.vtk_object = frac_vtk
        self.boundaries.vtk_object = bound_vtk

        # node_vtk = frac_net.extract_points(frac_net.point_data['type'] == 'nodes', include_cells=True)

    def add_fractures(self, fractures: Fractures):
        """
        Method used to add fractures to the FractureNetwork
        :param fractures: Fracture object
        """

        # If the FractureNetwork df is empty use this as the start.
        # If not then append the Fracture base entity df information to the
        # existing df
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
        """
        Method used to add boundaries to the FractureNetwork
        :param boundaries: Boundaries object
        """

        # If the FractureNetwork df is empty use this as the start.
        # If not then append the Boundary base entity df information to the
        # existing df
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
        """
        Method used to add nodes to the FractureNetwork
        :param nodes: Nodes object
        """

        # If the FractureNetwork df is empty use this as the start.
        # If not then append the Nodes base entity df information to the
        # existing df
        if self.entity_df is None:
            df = nodes.entity_df
        else:
            df = GeoDataFrame(
                pd.concat(
                    [self.entity_df,
                     nodes.entity_df[['type', 'geometry']]],
                    ignore_index=True)
            )
        self.nodes = nodes
        self.entity_df = df
