"""
In general, it would be good to give the possibility to trat separately sets of fractures/different types of nodes/
boundary and then everything together to consider the network as a compostion of single entities and not as a single
entity.

"""
import numpy as np
from geopandas import GeoDataFrame
import pandas as pd
from shapely.geometry import MultiLineString, Polygon, LineString, Point
from pyvista import PolyData, DataSet
from networkx import Graph
import fracability.Plotters as plts

import fracability.Representations as Rep
from fracability.AbstractClasses import BaseEntity


class Nodes(BaseEntity):
    """
    Node base entity, represents all the nodes in the network.
    """

    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        Each entity process the input dataframe in different ways
        Nodes modify the entity_df only to add the type column (if not
        already present)
        """

        self._df = gdf

        if 'type' not in self._df.columns:
            self._df['type'] = 'node'
        if 'node_type' not in self._df.columns:
            self._df['node_type'] = -9999

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.point_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):

        for index, point in enumerate(obj.points):
            self.entity_df.loc[self.entity_df['id'] == index, 'geometry'] = Point(point)

    @property
    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def matplot(self):
        plts.matplot_nodes(self)

    def vtkplot(self):
        plts.vtkplot_nodes(self)

    @property
    def node_count(self):

        nodes = self.vtk_object['node_type']
        unique, count = np.unique(nodes, return_counts=True)
        count_dict = dict(zip(unique, count))

        if count_dict[1] + count_dict[3] == 0:
            PI = 0
        else:
            PI = 100 * count_dict[1] / (count_dict[1] + count_dict[3])

        if count_dict[3] + count_dict[4] == 0:
            PY = 0
        else:
            PY = 100 * count_dict[3] / (count_dict[3] + count_dict[4])

        if count_dict[1] + count_dict[4] == 0:
            PX = 0
        else:
            PX = 100 * count_dict[4] / (count_dict[1] + count_dict[4])

        if count_dict[1] + count_dict[5] == 0:
            PU = 0
        else:
            PU = 100 * count_dict[5] / (count_dict[1] + count_dict[5])

        precise_n = 4 * (1 - PI / 100) / (1 - PX / 100)

        return PI, PY, PX, PU, precise_n


class Fractures(BaseEntity):
    """
    Base entity for fractures

    + Add method to choose different sets
    """
    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):

        self._df = gdf
        self._df.reset_index(inplace=True, drop=True)

        if 'type' not in self._df.columns:
            self._df['type'] = 'fracture'
        if 'censored' not in self._df.columns:
            self._df['censored'] = 0
        if 'set' not in self._df.columns:
            self._df['set'] = None

    @property
    def vtk_object(self) -> PolyData:
        df = self.entity_df
        vtk_obj = Rep.frac_bound_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):

        for region in set(obj['RegionId']):
            region = obj.extract_points(obj['RegionId'] == region)
            self.entity_df.loc[self.entity_df['id'] == region, 'geometry'] = LineString(region.points)

    @property
    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def matplot(self):
        plts.matplot_frac_bound(self)

    def vtkplot(self):
        plts.vtkplot_frac_bound(self)


class Boundary(BaseEntity):

    """
    Base entity for boundaries
    """
    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        Each entity process the input dataframe in different ways.
        Boundaries modify the entity_df by converting Polygons in Linestrings
        to (using the boundary method) and MultiLinestrings to LineStrings.
        A 'type' column is added if missing.
        """

        self._df = gdf
        self._df.reset_index(inplace=True, drop=True)

        geom_list = []
        # boundaries = df.boundary
        #
        # gdf = boundaries.explode(ignore_index=True)

        # The following is horrible and I hate it but for some reason the commented lines above
        # do not work for shapely 1.8 and geopandas 0.11 while they work perfectly with 2.0 and 0.13

        # This is to suppress the SettingWithCopyWarning (we are not working on a copy)
        pd.options.mode.chained_assignment = None

        for index, line in enumerate(self._df.loc[:, 'geometry']):
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
            self._df.loc[index, 'geometry'] = value
        # When PZero moves to shapely 2.0 remove the lines between the comments
        # and uncomment the two lines above

        if 'type' not in self._df.columns:
            self._df['type'] = 'boundary'

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.frac_bound_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):

        for region in set(obj['RegionId']):
            region = obj.extract_points(obj['RegionId'] == region)
            self.entity_df.loc[self.entity_df['id'] == region, 'geometry'] = LineString(region.points)

    @property
    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def matplot(self):
        plts.matplot_frac_bound(self)

    def vtkplot(self):
        plts.vtkplot_frac_bound(self)


class FractureNetwork(BaseEntity):
    """
    Fracture network base entity. Fracture networks are defined by one or
    more:

        + Fracture base entities

        + Boundary base entities

        + Nodes base entities

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
    def entity_df(self) -> GeoDataFrame:
        """
        Each entity is based on a geopandas dataframe. This property returns or sets
        the entity_df of the given entity.

        :getter: Returns the GeoDataFrame
        :setter: Sets the GeoDataFrame
        :type: GeoDataFrame

        Notes
        -------
        When set the dataframe is modified to conform to the assigned entity structure.
        """

        fractures_df = self.fractures.entity_df
        boundaries_df = self.boundaries.entity_df

        if self.nodes is not None:
            nodes_df = self.nodes.entity_df
            df = pd.concat([nodes_df, fractures_df, boundaries_df], ignore_index=True)
        else:
            df = pd.concat([fractures_df, boundaries_df], ignore_index=True)

        df['id'] = df.index

        return df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        FractureNetworks modify the entity_df by extracting the different types
        (fractures, boundaries, nodes). After that, the appropriate base entities
        are created and set.

        Notes
        -----
        This is an internal method that is called when a df is set.

        """

        # self._df = gdf
        nodes = Nodes(gdf.loc[gdf['type'] == 'node'])
        fractures = Fractures(gdf.loc[gdf['type'] == 'fracture'])
        boundary = Boundary(gdf.loc[gdf['type'] == 'boundary'])

        self.nodes = nodes
        self.fractures = fractures
        self.boundaries = boundary

        # print(self.boundaries.entity_df)

    @property
    def vtk_object(self) -> PolyData:
        df = self.entity_df
        vtk_obj = Rep.fracture_network_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):
        """
        FractureNetworks modify the vtkObject by extracting the different types
        (fractures, boundaries, nodes). After that, the appropriate vtkObject is
        set to the corresponding entity

        Notes
        -----
        This is an internal method that is called when a vtk is set.
        """

        frac_vtk = obj.extract_cells(obj.cell_data['type'] == 'fracture')
        bound_vtk = obj.extract_cells(obj.cell_data['type'] == 'boundary')
        node_vtk = obj.extract_points(obj.point_data['type'] == 'nodes', include_cells=False)

        self.fractures.vtk_object = frac_vtk
        self.boundaries.vtk_object = bound_vtk
        self.nodes.vtk_object = node_vtk

    @property
    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def matplot(self):
        plts.matplot_frac_net(self)

    def vtkplot(self):
        plts.vtkplot_frac_net(self)

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

        :param frac_obj:  Fracture object to be set
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

    def add_fractures(self, fractures: list, name: str = None):

        """
        Method used to add fractures to the FractureNetwork

        :param fractures: Fracture object
        :param name: Name of the fractures added (for example set_1). By default is None
        """

        new_df = GeoDataFrame(columns=fractures[0].entity_df.columns, crs=fractures[0].entity_df.crs)

        for i, fracture_obj in enumerate(fractures):
            obj_df = fracture_obj.entity_df
            obj_df['set'] = i+1
            new_df = pd.concat([new_df, obj_df], ignore_index=True)

        new_fractures = Fractures(new_df)
        self.fractures = new_fractures

    def add_boundaries(self, boundaries: Boundary):
        """
        Method used to add boundaries to the FractureNetwork

        :param boundaries: Boundaries object
        """

        self.boundaries = boundaries

    def add_nodes(self, nodes: Nodes):
        """
        Method used to add nodes to the FractureNetwork

        :param nodes: Nodes object
        """

        # If the FractureNetwork df is empty use this as the start.
        # If not then append the Nodes base entity df information to the
        # existing df

        self.nodes = nodes
