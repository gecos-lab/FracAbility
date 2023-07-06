"""
In general, it would be good to give the possibility to trat separately sets of fractures/different types of nodes/
boundary and then everything together to consider the network as a compostion of single entities and not as a single
entity.

"""
import numpy as np
from geopandas import GeoDataFrame
import pandas as pd
from pandas import DataFrame
from shapely.geometry import MultiLineString, Polygon, LineString, Point
from pyvista import PolyData, DataSet
from networkx import Graph
import fracability.Plotters as plts

import fracability.Adapters as Rep
from fracability.AbstractClasses import BaseEntity


class Nodes(BaseEntity):
    """
    Node base entity, represents all the nodes in the network.
    """

    def __init__(self, gdf: GeoDataFrame = None, node_type: int = -9999):

        self.node_type = node_type
        super().__init__(gdf)

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
            self._df['node_type'] = self.node_type

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.node_vtk_rep(df)
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

        if 1 in count_dict.keys():
            I_nodes = count_dict[1]
        else:
            I_nodes = 0

        if 3 in count_dict.keys():
            Y_nodes = count_dict[3]
        else:
            Y_nodes = 0

        if 4 in count_dict.keys():
            X_nodes = count_dict[4]
        else:
            X_nodes = 0

        if 5 in count_dict.keys():
            U_nodes = count_dict[5]
        else:
            U_nodes = 0

        if 6 in count_dict.keys():
            Y2_nodes = count_dict[6]
        else:
            Y2_nodes = 0


        tot_Y_nodes = Y_nodes+Y2_nodes

        if I_nodes + tot_Y_nodes == 0:
            PI = 0
        else:
            PI = 100 * I_nodes / (I_nodes + tot_Y_nodes)

        if tot_Y_nodes + X_nodes == 0:
            PY = 0
        else:
            PY = 100 * tot_Y_nodes / (tot_Y_nodes + X_nodes)

        if I_nodes + X_nodes == 0:
            PX = 0
        else:
            PX = 100 * X_nodes / (I_nodes + X_nodes)

        if I_nodes + U_nodes == 0:
            PU = 0
        else:
            PU = 100 * U_nodes / (I_nodes + U_nodes)

        precise_n = 4 * (1 - PI / 100) / (1 - PX / 100)

        return PI, PY, PX, PU, precise_n

    def ternary_plot(self):
        plts.matplot_ternary(self)


class Fractures(BaseEntity):
    """
    Base entity for fractures

    + Add method to activate different sets
    + Add method to plot rose diagram
    """

    def __init__(self, gdf: GeoDataFrame = None, set_n: int = None):

        self.set_n = set_n
        super().__init__(gdf)

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
            self._df['set'] = self.set_n

    @property
    def vtk_object(self) -> PolyData:
        df = self.entity_df
        vtk_obj = Rep.frac_vtk_rep(df)
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
        plts.vtkplot_fractures(self)


class Boundary(BaseEntity):

    """
    Base entity for boundaries
    """
    def __init__(self, gdf: GeoDataFrame = None, group_n: int = 0):

        self.group_n = group_n
        super().__init__(gdf)

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
        if 'group' not in self._df.columns:
            self._df['group'] = self.group_n

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.bound_vtk_rep(df)
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
        plts.vtkplot_boundaries(self)


class FractureNetwork:
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

    def __init__(self):
        self.column_names = ['type', 'object', 'node_type', 'fracture_set', 'boundary_group', 'active']
        self._df: DataFrame = DataFrame(columns=self.column_names)

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gpd: GeoDataFrame):
        
        nodes = gpd.loc[gpd['type'] == 'nodes']

        if not nodes.empty:

            types = set(nodes['node_type'])

            for node_type in types:
                nodes = Nodes(nodes.loc[nodes['node_type'] == node_type], node_type)
                if self.is_set_active(node_type):
                    self.add_nodes(nodes)

        fractures = gpd.loc[gpd['type'] == 'fracture']

        if not fractures.empty:
            sets = set(fractures['set'])

            for set_n in sets:
                fracture = Fractures(fractures.loc[fractures['set'] == set_n], set_n)
                if self.is_set_active(set_n):
                    self.add_fractures(fracture)

        boundaries = gpd.loc[gpd['type'] == 'boundary']

        if not boundaries.empty:

            groups = set(boundaries['group'])

            for group_n in groups:
                boundary = Boundary(boundaries.loc[boundaries['group'] == group_n], group_n)
                if self.is_group_active(group_n):
                    self.add_boundaries(boundary)

    #  ==================== Nodes property ====================

    @property
    def nodes(self) -> Nodes:
        """
        Property that returns a Node entity object of all the active nodes.
        :return: Nodes entity object
        """
        return Nodes(self._active_nodes_df)

    @property
    def _nodes_components(self) -> DataFrame:
        """
        Property that returns the nodes components of the Fracture network df.
        :return: Pandas dataframe slice of the nodes components
        """
        nodes = self.entity_df.loc[self.entity_df['type'] == 'nodes']
        return nodes

    @property
    def _active_nodes_components(self) -> DataFrame:
        """
        Internal property that returns the active nodes components in the of the Fracture network df
        :return: Pandas dataframe slice of active nodes components
        """
        nodes = self.entity_df.loc[self.entity_df['type'] == 'nodes']

        active_nodes = nodes.loc[nodes['active'] == 1]
        return active_nodes

    @property
    def _active_nodes_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active nodes
        :return:
        """

        gdf = GeoDataFrame()

        nodes = self._active_nodes_components

        for row, fracture in nodes.iterrows():
            gdf = pd.concat([gdf, fracture['object'].entity_df], ignore_index=True)

        return gdf

    def add_nodes(self, nodes: Nodes = None):
        """
        Method used to add nodes components to the fracture network Dataframe
        :param nodes: Nodes object to be added

        Notes
        -------
        The nodes are added to the fracture network dataframe using the assigned node_type present in the
        Nodes object dataframe. If the node type is already present the node object will be overwritten if not it will
        be appended
        """

        node_type = list(set(nodes.entity_df['node_type']))[0]

        if node_type not in self._df['node_type'].values:
            new_df = DataFrame([['nodes', nodes, node_type, 1]], columns=['type', 'object',
                                                                          'node_type', 'active'])
            self._df = pd.concat([self._df, new_df], ignore_index=True)
        else:
            self._df.loc[self._df['node_type'] == node_type, 'object'] = nodes

    def nodes_object(self, node_type: int) -> Nodes:
        """
        Method that returns the Node object of a given node_type
        :param node_type: Type of the node
        :return: Nodes object
        """
        return self._fractures_components.loc[self._fractures_components['node_type'] == node_type, 'object'].values[0]

    def activate_nodes(self, node_type: list = None):
        """
        Method that activates the nodes provided in the node_type list.
        :param node_type: List of node types to be activated
        """

        if node_type is None:
            self.entity_df.loc[self.entity_df['type'] == 'nodes', 'active'] = 1
        else:
            self.entity_df.loc[self.entity_df['type'] == 'nodes', 'active'] = 0
            for t in node_type:
                self.entity_df.loc[self.entity_df['node_type'] == t, 'active'] = 1

    def is_type_active(self, node_type: int) -> bool:
        """
        Method used to return if a given node type is active in the fracture network
        :param node_type: node type to check
        :return: Bool value of the test
        """
        active_nodes = self._active_nodes_components

        value = active_nodes.loc[active_nodes['node_type'] == node_type, 'active'].values[0]

        return value

    #  ==================== Fractures  ====================

    @property
    def fractures(self) -> Fractures:
        """
        Property that returns a Fracture entity object of all the active fracture sets.
        :return: Fracture entity object
        """
        return Fractures(self._active_fractures_df)

    @property
    def _fractures_components(self) -> DataFrame:
        """
        Internal property that returns the fracture components of the Fracture network df.
        :return: Pandas dataframe slice of the fracture set components
        """
        fractures = self.entity_df.loc[self.entity_df['type'] == 'fractures']
        return fractures

    @property
    def _active_fractures_components(self) -> DataFrame:
        """
        Internal property that returns the active fracture components in the of the Fracture network df
        :return: Pandas dataframe slice of active fracture components
        """

        fractures = self.entity_df.loc[self.entity_df['type'] == 'fractures']

        active_fractures = fractures.loc[fractures['active'] == 1]
        return active_fractures

    @property
    def _active_fractures_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active fractures sets components
        :return: Geopandas dataframe of the active fracture sets components
        """

        gdf = GeoDataFrame()

        fractures = self._active_fractures_components

        for row, fracture in fractures.iterrows():
            gdf = pd.concat([gdf, fracture['object'].entity_df], ignore_index=True)

        return gdf

    def add_fractures(self, fractures: Fractures = None):
        """
        Method used to add fracture components to the fracture network Dataframe
        :param fractures: Fracture object to be added

        Notes
        -------
        The fractures are added to the fracture network dataframe using the assigned fracture_set present in the
        Fracture object dataframe. If the set is already present the fracture object will be overwritten if not it will
        be appended
        """

        set_n = list(set(fractures.entity_df['set']))[0]

        if set_n not in self._df['fracture_set'].values:
            new_df = DataFrame([['fractures', fractures, set_n, 1]], columns=['type', 'object',
                                                                              'fracture_set', 'active'])
            self._df = pd.concat([self._df, new_df], ignore_index=True)
        else:
            self._df.loc[self._df['fracture_set'] == set_n, 'object'] = fractures

    def fracture_object(self, set_n: int) -> Fractures:
        """
        Method that returns the Fracture object of a given set
        :param set_n: Number of the set
        :return: Fracture object
        """
        return self._fractures_components.loc[self._fractures_components['fracture_set'] == set_n, 'object'].values[0]

    def activate_fractures(self, set_n: list = None):
        """
        Method that activates the fractures provided in the set_n list.
        :param set_n: List of sets to be activated
        """

        if set_n is None:
            self.entity_df.loc[self.entity_df['type'] == 'fractures', 'active'] = 1
        else:
            self.entity_df.loc[self.entity_df['type'] == 'fractures', 'active'] = 0
            for n in set_n:
                self.entity_df.loc[self.entity_df.fracture_set == n, 'active'] = 1

    def is_set_active(self, set_n: int) -> bool:
        """
        Method used to return if a given fracture set is active in the fracture network
        :param set_n: set to check
        :return: Bool value of the test
        """

        active_fractures = self._active_fractures_components

        value = active_fractures.loc[active_fractures['fracture_set'] == set_n, 'active'].values[0]

        return value

    #  ==================== Boundaries property ====================

    @property
    def boundaries(self) -> Boundary:
        """
        Property that returns a Boundary entity object of all the active boundary groups.
        :return: Boundary entity object
        """
        return Boundary(self._active_boundaries_df)

    @property
    def _boundaries_components(self) -> DataFrame:
        """
        Internal property that returns the boundary components of the Fracture network df.
        :return: Pandas dataframe slice of the boundary groups components
        """

        boundaries = self.entity_df.loc[self.entity_df['type'] == 'boundary']
        return boundaries

    @property
    def _active_boundaries_components(self) -> DataFrame:
        """
        Internal property that returns the active boundary group components in the of the Fracture network df
        :return: Pandas dataframe slice of active boundary group components
        """

        boundaries = self.entity_df.loc[self.entity_df['type'] == 'boundary']

        active_boundaries = boundaries.loc[boundaries['active'] == 1]

        return active_boundaries

    @property
    def _active_boundaries_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active boundary
        :return: GeoPandas DataFrame of the active boundaries of the fracture network
        """

        df = GeoDataFrame()

        boundaries = self._active_boundaries_components

        for row, fracture in boundaries.iterrows():
            df = pd.concat([df, fracture['object'].entity_df], ignore_index=True)

        return df

    def add_boundaries(self, boundary: Boundary = None):
        """
        Method used to add boundary components to the fracture network Dataframe
        :param boundary: Boundary object to be added

        Notes
        -------
        The boundary are added to the fracture network dataframe using the assigned group_n present in the
        Boundary object dataframe. If the group is already present the boundary object will be overwritten if not it will
        be appended
        """

        group_n = list(set(boundary.entity_df['group']))[0]

        if group_n not in self._df['boundary_group']:

            new_df = DataFrame([['boundary', boundary, group_n, 1]], columns=['type', 'object',
                                                                              'boundary_group', 'active'])
            self._df = pd.concat([self._df, new_df], ignore_index=True)
        else:
            self._df.loc[self._df['boundary_group'] == group_n, 'object'] = boundary

    def boundary_object(self, group_n: int) -> Fractures:
        """
        Method that returns the Node object of a given group_number
        :param group_n: Number of the group
        :return: Boundary object
        """

        return self._boundaries_components.loc[self._fractures_components['fracture_set'] == group_n, 'object'].values[0]

    def activate_boundaries(self, group_n: list = None):

        """
        Method that activates the boundary provided in the group_n list.
        :param group_n: List of groups to be activated
        """

        if group_n is None:
            self.entity_df.loc[self.entity_df['type'] == 'boundary', 'active'] = 1
        else:
            self.entity_df.loc[self.entity_df['type'] == 'boundary', 'active'] = 0
            for n in group_n:
                self.entity_df.loc[self.entity_df.fracture_set == n, 'active'] = 1

    def is_group_active(self, group_n: int) -> bool:
        """
        Method used to return if a given boundary group is active in the fracture network
        :param group_n: set to check
        :return: Bool value of the test
        """

        active_boundaries = self._active_boundaries_components
        value = active_boundaries.loc[active_boundaries['boundary_group'] == group_n, 'active'].values[0]

        return value

    #  ==================== Generic methods ====================

    def fracture_network_to_components_df(self) -> GeoDataFrame:

        """
        Method used to return the fracture network as a single geopandas dataframe.
        :return: Geopandas DataFrame of the whole fracture network
        """

        gdf = GeoDataFrame()

        nodes = self._active_nodes_df

        gdf = pd.concat([gdf, nodes], ignore_index=True)

        fractures = self._active_fractures_df

        gdf = pd.concat([gdf, fractures], ignore_index=True)

        boundaries = self._active_boundaries_df

        gdf = pd.concat([gdf, boundaries], ignore_index=True)

        return gdf

    def vtk_object(self, include_nodes: bool = True) -> PolyData:

        """
        Method used to return a vtkPolyData representation of the fracture network
        :param include_nodes: Bool flag used to control if include or not the nodes in the fracture network object
        :return: vtkPolyData of the fracture network
        """

        vtk_obj = Rep.fracture_network_vtk_rep(self.fracture_network_to_components_df(), include_nodes=include_nodes)
        return vtk_obj

    #  ==================== Plotting methods ====================

    @property
    def network_object(self) -> Graph:
        """
        Method used to return a networkx Graph representation of the fracture network
        :return: Graph of the fracture network
        """

        network_object = Rep.networkx_rep(self.vtk_object(include_nodes=False))
        return network_object

    def vtkplot(self):
        """
        Method used to plot the fracture network using vtk
        :return:
        """

        plts.vtkplot_frac_net(self)

    def matplot(self):
        """
        Method used to plot the fracture network using matplotlib
        :return:
        """
        plts.matplot_frac_net(self)

    def plot_ternary(self):
        """
        Method used to plot the ternary diagram of the fracture network
        :return:
        """
        plts.matplot_ternary(self)

