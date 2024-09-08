"""
In general, it would be good to give the possibility to treat separately sets of fractures/different types of nodes/
boundary and then everything together to consider the network as a composition of single entities and not as a single
entity.

todo make somehow nodes and fractures connected so that for example when only a set is displayed only the nodes of the corresponding set are considered
"""
import os.path

import numpy as np
from geopandas import GeoDataFrame, GeoSeries, read_file
import pandas as pd
from pandas import DataFrame
from shapely.geometry import MultiLineString, Polygon, LineString, Point, MultiPoint
from pyvista import PolyData, DataSet, wrap
from networkx import Graph
from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

import fracability.Plotters as plts

import fracability.Adapters as Rep
from fracability.AbstractClasses import BaseEntity
from fracability.operations import Geometry, Topology


class Nodes(BaseEntity):
    """
    Node base entity, represents all the nodes in the network.

    Parameters
    -----------
    gdf: GeoDataFrame
        Use as input a geopandas dataframe
    csv: str
        Use as input a csv indicated by the path
    shp: str
        Use as input a shapefile indicated by the path
    node_type: int
        Node type. I:1, Y:3, X:4, U:5

    Notes
    --------
    The csv needs to have a "geometry" column. If missing the import will fail.
    """

    def __init__(self, gdf: GeoDataFrame = None, csv: str = None, shp: str = None, node_type: int = -9999):

        self.node_type = node_type
        if gdf is not None:
            super().__init__(gdf=gdf)
        elif csv is not None:
            super().__init__(csv=csv)
        elif shp is not None:
            super().__init__(shp=shp)

    @property
    def entity_df(self) -> GeoDataFrame:
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        Each entity process the input dataframe in different ways.
        Nodes modify the entity_df only to add the type column (if not
        already present)
        """

        self._df = gdf
        columns = self._df.columns
        if 'og_line_id' not in columns:
            self._df['og_line_id'] = np.array(gdf.index.values+1)
        if 'type' not in columns:
            self._df['type'] = 'node'
        if 'n_type' not in columns:
            self._df['n_type'] = self.node_type

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.node_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):
        for index, point in enumerate(obj.points):
            self.entity_df.loc[self.entity_df['id'] == index, 'geometry'] = Point(point)

    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    @property
    def ternary_node_count(self) -> tuple[float, float, float, float, float]:
        """
        Calculate the node proportions and precise connectivity value following Manzocchi 2002
        :return: A tuple of values PI, PY, PX, PU, CI
        """
        count_dict = self.node_count

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

        tot_Y_nodes = Y_nodes + Y2_nodes

        if I_nodes + tot_Y_nodes == 0:
            PI = 0
        else:
            PI = 100 * I_nodes / (I_nodes + tot_Y_nodes + X_nodes)

        if tot_Y_nodes + X_nodes == 0:
            PY = 0
        else:
            PY = 100 * tot_Y_nodes / (I_nodes + tot_Y_nodes + X_nodes)

        if I_nodes + X_nodes == 0:
            PX = 0
        else:
            PX = 100 * X_nodes / (I_nodes + tot_Y_nodes + X_nodes)

        if I_nodes + U_nodes == 0:
            PU = 0
        else:
            PU = 100 * U_nodes / (I_nodes + tot_Y_nodes + X_nodes)

        precise_n = 4 * (1 - PI / 100) / (1 - PX / 100)

        return PI, PY, PX, PU, precise_n

    @property
    def node_count(self) -> dict:
        """
        Calculate the node count dictionary

        :return: A dictionary of nodes and their count
        """

        nodes = self.vtk_object['n_type']
        unique, count = np.unique(nodes, return_counts=True)
        count_dict = dict(zip(unique, count))
        return count_dict
    @property
    def n_censored(self) -> int:
        """ Return the number of censored nodes"""

        nodes = self.vtk_object['n_type']
        unique, count = np.unique(nodes, return_counts=True)
        count_dict = dict(zip(unique, count))

        if 5 not in count_dict.keys():
            return 0
        else:
            return count_dict[5]

    @property
    def n_complete(self) -> int:
        """ Return the number of I nodes"""

        nodes = self.vtk_object['n_type']
        unique, count = np.unique(nodes, return_counts=True)
        count_dict = dict(zip(unique, count))

        return count_dict[1]

    def node_origin(self, node_type: int) -> GeoSeries:
        """
        Return the node origin for the given node type (i.e. which set/sets is/are associated to the node)
        :param node_type:
        :return:
        """
        return self.entity_df.loc[self.entity_df['n_type'] == node_type, 'n_origin']

    def mat_plot(self, markersize=7, return_plot=False, show_plot=True):
        """
        Plot Nodes object with matplot
        :param markersize:
        :param return_plot:
        :param show_plot:
        :return:
        """
        plts.matplot_nodes(self, markersize, return_plot, show_plot)

    def vtk_plot(self, markersize=7, return_plot=False, show_plot=True, notebook=True):
        """
        Plot Nodes object with VTK
        :param markersize:
        :param return_plot:
        :param show_plot:
        :return:
        """

        plts.vtkplot_nodes(self, markersize, return_plot, show_plot, notebook=notebook)

    def ternary_plot(self):
        plts.matplot_ternary(self)


class Fractures(BaseEntity):
    """
    Base entity for fractures, represents all the fractures in the network.

    Parameters
    -----------
    gdf: GeoDataFrame
        Use as input a geopandas dataframe
    csv: str
        Use as input a csv indicated by the path
    shp: str
        Use as input a shapefile indicated by the path
    set_n: int
        Fracture set number.
    check_geometry: Bool
        Perform geometry check. Default is False


    Notes
    --------
    + The csv needs to have a "geometry" column. If missing the import will fail.
    + If the input csv or shapefile has an f_set column then the set_n will be ignored
    """

    def __init__(self, gdf: GeoDataFrame = None, csv: str = None,
                 shp: str = None, set_n: int = None,
                 check_geometry: bool = False):

        self.check_geometries_flag = check_geometry
        self._set_n = set_n
        if gdf is not None:
            super().__init__(gdf=gdf)
        elif csv is not None:
            super().__init__(csv=csv)
        elif shp is not None:
            super().__init__(shp=shp)
        else:
            super().__init__()

    @property
    def set_n(self) -> int:
        """
        Get the set number
        """
        return self._set_n

    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gdf: GeoDataFrame):
        """
        Each entity process the input dataframe in different ways.
        Fractures modify the entity_df in a couple of ways:
            + No Multilines can be used.
            + If not f_set column is present, it will be created following the set_n value
            + If no length column is present, it will be created (with length rounded to the 4th decimal point)
            + If no censoring column is present, it will be created setting all values to 0
        """
        multiline_list = []
        for index, geom in zip(gdf.index, gdf['geometry']):  # For each geometry in the df

            if isinstance(geom, MultiLineString):
                multiline_list.append(index)
                continue
        if len(multiline_list) > 0:
            print(f'Multilines found, removing from database. If necessary correct them: {np.array(multiline_list)+1}')

        gdf.drop(multiline_list, inplace=True)

        self._df = gdf.copy()
        self._df.reset_index(inplace=True, drop=True)
        columns = self._df.columns
        if 'og_line_id' not in columns:
            self._df['og_line_id'] = np.array(gdf.index.values+1)
        if 'type' not in columns:
            self._df['type'] = 'fracture'
        if 'censored' not in columns:
            self._df['censored'] = 0
        if 'f_set' not in columns:  # todo change this to "set_n" and check at least for similar names
            self._df['f_set'] = self.set_n
        if 'length' not in columns:
            self._df['length'] = np.round(self._df['geometry'].length, 4)

        if self.check_geometries_flag:
            self.remove_double_points()
            self.check_geometries()

    @property
    def vtk_object(self) -> PolyData:
        df = self.entity_df
        vtk_obj = Rep.frac_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):
        if 'RegionId' not in obj.array_names:
            regions_ids = np.arange(0, obj.n_cells)
            obj['RegionId'] = regions_ids

        if not self.entity_df.empty:
            for region_id in set(obj['RegionId']):
                region = obj.extract_points(obj['RegionId'] == region_id)
                self.entity_df.loc[self.entity_df['id'] == region, 'geometry'] = LineString(region.points)
        else:
            idx = list(set(obj['RegionId']))
            geometry = []
            for region_id in idx:
                region = wrap(obj.extract_cells(obj['RegionId'] == region_id))
                index_list, ind = np.unique(region.cell_connectivity, return_index=True)
                index_list = index_list[np.argsort(ind)]
                geometry.append(LineString(region.points[index_list]))
            d = {'id': idx, 'geometry': geometry}
            gdf = GeoDataFrame(d)
            self.entity_df = gdf

    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def check_geometries(self, remove_dup=True, save_shp=False):
        """
        Method used to check if the geometries are correct i.e.:
        + No repeating points
        + No overlaps

        By default, the method will return a list of geometries that need to be fixed. Additionally, a shp file can be
        saved with only the geometries that need to be corrected.

        :param remove_dup: Automatically remove duplicate points. By default, True
        :param save_shp: Save in the same folder of the input shp with only the geometries that need to be corrected.
                         This is a useful support file to be imported in gis to quickly find the problematic geometries.
                         False by default. todo to be implemented
        """

        overlaps_list = []
        tot_geom = len(self.entity_df.geometry)
        print('\n\n')
        for line, geom in enumerate(self.entity_df.geometry):
            print(f'Checking geometries: {line}/{tot_geom}',end='\r')
            if geom is None:
                print(f"\n\nWarning, empty geometry at line {line+1}, fix in GIS\n\n")
            overlaps = self.entity_df.overlaps(geom)
            if overlaps.any():
                overlaps_list.append(self.entity_df.loc[line, 'og_line_id'])
        if len(overlaps_list) > 0:
            print(f'\n\nDetected overlaps for set {self._set_n}: {overlaps_list}. Check geometries in gis and fix.\n\n')

    def mat_plot(self,
                 linewidth=1,
                 color='black',
                 color_set=False,
                 return_plot=False,
                 show_plot=True):
        """
        Plot fracture object with matplotlib

        :param linewidth:
        :param color:
        :param color_set:
        :param return_plot:
        :param show_plot:
        :return:
        """

        plts.matplot_fractures(self,
                               linewidth,
                               color,
                               color_set,
                               return_plot,
                               show_plot)

    def vtk_plot(self,
                 linewidth=1,
                 color='black',
                 color_set=False,
                 return_plot=False,
                 show_plot=True,
                 display_property: str = None,
                 notebook=True):
        """
        Plot fracture object with VTK
        :param linewidth:
        :param color:
        :param color_set:
        :param return_plot:
        :param show_plot:
        :param display_property:
        :return:
        """
        plts.vtkplot_fractures(self,
                               linewidth=linewidth,
                               color=color,
                               color_set=color_set,
                               return_plot=return_plot,
                               show_plot=show_plot,
                               display_property=display_property,
                               notebook=notebook)


class Boundary(BaseEntity):

    """
    Base entity for boundaries, represents all the boundaries in the network.

    Parameters
    -----------
    gdf: GeoDataFrame
        Use as input a geopandas dataframe
    csv: str
        Use as input a csv indicated by the path
    shp: str
        Use as input a shapefile indicated by the path
    group_n: int
        Boundary number.
    check_geometry: Bool
        Perform geometry check. Default is False



    Notes
    --------
    + The csv needs to have a "geometry" column. If missing the import will fail.
    """
    def __init__(self, gdf: GeoDataFrame = None,
                 csv: str = None, shp: str = None,
                 group_n: int = 1, check_geometry: bool = False):
        """
        Init for Boundary entity. Different inputs can be used. Geopandas dataframe, csv or shapefile. The csv needs to be
        structured in such a way to be compatible with the Nodes entity.

        :param gdf: Geopandas dataframe
        :param csv: Path of a csv
        :param shp: Path of the shapefile
        :param group_n: Boundary group number
        """

        self.group_n = group_n
        self.check_geometries_flag = check_geometry
        if gdf is not None:
            super().__init__(gdf=gdf)
        elif csv is not None:
            super().__init__(csv=csv)
        elif shp is not None:
            super().__init__(shp=shp)


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
        # When PZero moves to shapely 2.0 remove the lines between these comments
        # and uncomment the two lines above

        # Remove from here
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
        # Remove up to here

        columns = self._df.columns
        if 'og_line_id' not in columns:
            self._df['og_line_id'] = np.array(gdf.index.values+1)
        if 'type' not in columns:
            self._df['type'] = 'boundary'
        if 'b_group' not in columns:
            self._df['b_group'] = self.group_n

        if self.check_geometries_flag:
            self.remove_double_points()

    @property
    def vtk_object(self) -> PolyData:

        df = self.entity_df
        vtk_obj = Rep.bound_vtk_rep(df)
        return vtk_obj

    @vtk_object.setter
    def vtk_object(self, obj: DataSet):

        if 'RegionId' not in obj.array_names:
            regions_ids = np.arange(0, obj.n_cells)
            obj['RegionId'] = regions_ids

        if not self.entity_df.empty:
            for region_id in set(obj['RegionId']):
                region = obj.extract_points(obj['RegionId'] == region_id)
                points = region.points
                if points[0] != points[-1]:  # All boundaries must be closed
                    points = np.append(points, [points[0]], axis=0)

                self.entity_df.loc[self.entity_df['id'] == region, 'geometry'] = LineString(points)
        else:
            idx = list(set(obj['RegionId']))
            geometry = []
            for region_id in idx:
                region = obj.extract_cells(obj['RegionId'] == region_id)
                points = region.points
                if np.any(points[0, :] != points[-1, :]):  # All boundaries must be closed
                    points = np.append(points, [points[0]], axis=0)
                geometry.append(LineString(points))

            d = {'id': idx, 'geometry': geometry}
            gdf = GeoDataFrame(d)
            self.entity_df = gdf

    def network_object(self) -> Graph:
        network_obj = Rep.networkx_rep(self.vtk_object)
        return network_obj

    def mat_plot(self,
                 linewidth=1,
                 color='red',
                 return_plot=False,
                 show_plot=True):
        """
        Plot Boundary object with matplotlib
        :param linewidth:
        :param color:
        :param return_plot:
        :param show_plot:
        :return:
        """

        plts.matplot_boundaries(self,
                                linewidth,
                                color,
                                return_plot,
                                show_plot)

    def vtk_plot(self,
                 linewidth=1,
                 color='red',
                 color_set=False,
                 return_plot=False,
                 show_plot=True,
                 notebook=True):
        """
        Plot Boundary object with vtk
        :param linewidth:
        :param color:
        :param color_set:
        :param return_plot:
        :param show_plot:
        :return:
        """
        plts.vtkplot_boundaries(self,
                                linewidth=linewidth,
                                color=color,
                                return_plot=return_plot,
                                show_plot=show_plot,
                                notebook=notebook)


class Backbone(Fractures):
    """
    Base entity for the backbone. It inherits the same properties of Fractures and is made to differentiate the two types and in case add backbone specific methods/properties if needed
    """
    def __init__(self, gdf: GeoDataFrame = None, csv: str = None,
                 shp: str = None, set_n: int = None,
                 check_geometry: bool = False):
        super().__init__(gdf, csv, shp, set_n, check_geometry)


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

    def __init__(self, gdf: GeoDataFrame = None, csv: str = None):
        """
        Init for fracture network entity. Different inputs can be used. Geopandas dataframe, csv or shapefile.
        The csv needs to be structured in such a way to be compatible with the Nodes entity.

        :param gdf: Geopandas dataframe
        :param csv: Path of a csv
        """

        self.column_names = ['type', 'object', 'n_type', 'f_set', 'b_group', 'active']
        self._df: DataFrame = DataFrame(columns=self.column_names)

        if csv is not None:
            gdf = read_file(csv, GEOM_POSSIBLE_NAMES="geometry", KEEP_GEOM_COLUMNS="NO")

        if gdf is not None:
            nodes = Nodes(gdf.loc[gdf['type'] == 'node'])
            fractures = Fractures(gdf.loc[gdf['type'] == 'fracture'])
            boundaries = Boundary(gdf.loc[gdf['type'] == 'boundary'])

            self.add_nodes(nodes)
            self.add_fractures(fractures)
            self.add_boundaries(boundaries)

    @property
    def entity_df(self):
        return self._df

    @entity_df.setter
    def entity_df(self, gpd: GeoDataFrame):

        nodes = gpd.loc[gpd['type'] == 'nodes']

        if not nodes.empty:

            types = set(nodes['node_type'])

            for node_type in types:
                nodes = Nodes(gdf=nodes.loc[nodes['n_type'] == node_type], node_type=node_type)
                if self.is_type_active(node_type):
                    self.add_nodes(nodes)

        fractures = gpd.loc[gpd['type'] == 'fracture']

        if not fractures.empty:
            sets = set(fractures['f_set'])

            for set_n in sets:
                fracture = Fractures(gdf=fractures.loc[fractures['f_set'] == set_n], set_n=set_n)
                if self.is_set_active(set_n):
                    self.add_fractures(fracture)

        boundaries = gpd.loc[gpd['type'] == 'boundary']

        if not boundaries.empty:

            groups = set(boundaries['b_group'])

            for group_n in groups:
                boundary = Boundary(gdf=boundaries.loc[boundaries['b_group'] == group_n], group_n=group_n)
                if self.is_group_active(group_n):
                    self.add_boundaries(boundary)

    @property
    def crs(self):
        return self.fracture_network_to_components_df().crs

    #  ==================== Nodes property ====================

    @property
    def nodes(self) -> Nodes:
        """
        Property that returns a Node entity object of all the active nodes.
        :return: Nodes entity object
        """
        if self._active_nodes_df is not None:
            return Nodes(self._active_nodes_df)
        else:
            return None

    @property
    def _nodes_components(self) -> DataFrame:
        """
        Property that returns the nodes components of the Fracture network df.
        :return: Pandas dataframe slice of the nodes components
        """
        nodes = self.entity_df.loc[self.entity_df['type'] == 'nodes']
        if not nodes.empty:
            return nodes
        else:
            return None

    @property
    def _active_nodes_components(self) -> DataFrame:
        """
        Internal property that returns the active nodes components in the of the Fracture network df
        :return: Pandas dataframe slice of active nodes components
        """
        nodes = self.entity_df.loc[self.entity_df['type'] == 'nodes']

        active_nodes = nodes.loc[nodes['active'] == 1]

        if not active_nodes.empty:
            return active_nodes
        else:
            return None

    @property
    def _active_nodes_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active nodes
        :return:
        """

        gdf = GeoDataFrame()

        nodes = self._active_nodes_components

        if nodes is not None:
            for row, fracture in nodes.iterrows():
                gdf = pd.concat([gdf, fracture['object'].entity_df], ignore_index=True)
            return gdf
        else:
            return None

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

        node_types = set(nodes.entity_df['n_type'])

        for node_type in node_types:

            nodes_df = nodes.entity_df.loc[nodes.entity_df['n_type'] == node_type]

            nodes_group = Nodes(gdf=nodes_df, node_type=node_type)

            if node_type not in self._df['n_type'].values:
                new_df = DataFrame([['nodes', nodes_group, node_type, 1]], columns=['type', 'object',
                                                                                    'n_type', 'active'])
                self._df = pd.concat([self._df, new_df], ignore_index=True)
            else:
                self._df.loc[self._df['n_type'] == node_type, 'object'] = nodes_group

    def add_nodes_from_dict(self, node_dict, classes=None, origin_dict: dict = None):
        """Add nodes a dict of shapely geometry (key), classes and optionally node origin (value).

        :param node_dict: Dict of shapely node geometries as keys and a list (class, node_index).
        :param classes: List of node classes that are needed to be added. If none are provided all the classes are used [1, 3, 4, 5, 6]
        :param origin_dict: Dict of shapely node geometries as keys and a list of node origin.
        """

        node_geometry = np.array(list(node_dict.keys()))
        class_list = np.array(list(node_dict.values()))
        origin_list = list(origin_dict.values())

        entity_df = GeoDataFrame({'type': 'node', 'n_type': class_list[:, 0], 'n_index': class_list[:, 1],
                                  'n_origin': origin_list, 'geometry': node_geometry}, crs=self.crs)

        nodes = Nodes(gdf=entity_df)

        self.add_nodes(nodes)

    def nodes_object(self, node_type: int) -> Nodes:
        """
        Method that returns the Node object of a given node_type
        :param node_type: Type of the node
        :return: Nodes object
        """
        return self._fractures_components.loc[self._fractures_components['n_type'] == node_type, 'object'].values[0]

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
                self.entity_df.loc[self.entity_df['n_type'] == t, 'active'] = 1

    def is_type_active(self, node_type: int) -> bool:
        """
        Method used to return if a given node type is active in the fracture network
        :param node_type: node type to check
        :return: Bool value of the test
        """
        nodes = self._nodes_components

        value = nodes.loc[nodes['n_type'] == node_type, 'active'].values[0]

        return value

    #  ==================== Fractures  ====================

    @property
    def fractures(self) -> Fractures:
        """
        Property that returns a Fracture entity object of all the active fracture sets.
        :return: Fracture entity object
        """
        if self._active_fractures_df is not None:
            return Fractures(self._active_fractures_df)
        return None

    @property
    def sets(self) -> list:
        """Return the list of the number of sets"""

        sets = list(set(self.fractures.entity_df['f_set'].values))
        return sets

    @property
    def _fractures_components(self) -> DataFrame:
        """
        Internal property that returns the fracture components of the Fracture network df.
        :return: Pandas dataframe slice of the fracture set components
        """
        fractures = self.entity_df.loc[self.entity_df['type'] == 'fractures']

        if not fractures.empty:
            return fractures
        else:
            return None

    @property
    def _active_fractures_components(self) -> DataFrame:
        """
        Internal property that returns the active fracture components in the of the Fracture network df
        :return: Pandas dataframe slice of active fracture components
        """

        fractures = self.entity_df.loc[self.entity_df['type'] == 'fractures']

        active_fractures = fractures.loc[fractures['active'] == 1]
        if not active_fractures.empty:
            return active_fractures
        else:
            return None

    @property
    def _active_fractures_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active fractures sets components
        :return: Geopandas dataframe of the active fracture sets components
        """

        gdf = GeoDataFrame()

        fractures = self._active_fractures_components

        if fractures is not None:
            for row, fracture in fractures.iterrows():
                gdf = pd.concat([gdf, fracture['object'].entity_df], ignore_index=True)

            return gdf
        else:
            return None

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
        fracture_sets = set(fractures.entity_df['f_set'])

        for set_n in fracture_sets:

            fractures_df = fractures.entity_df.loc[fractures.entity_df['f_set'] == set_n]
            fractures_group = Fractures(gdf=fractures_df, set_n=set_n)

            if set_n not in self._df['f_set'].values:
                new_df = DataFrame([['fractures', fractures_group, set_n, 1]],
                                   columns=['type', 'object', 'f_set', 'active'])
                self._df = pd.concat([self._df, new_df], ignore_index=True)
            else:
                self._df.loc[self._df['f_set'] == set_n, 'object'] = fractures_group

    def fracture_object(self, set_n: int) -> Fractures:
        """
        Method that returns the Fracture object of a given set
        :param set_n: Number of the set
        :return: Fracture object
        """
        return self._fractures_components.loc[self._fractures_components['f_set'] == set_n, 'object'].values[0]

    def activate_fractures(self, set_n: list = None):
        """
        Method that activates the fractures provided in the set_n list.
        :param set_n: List of sets to be activated
        """

        if set_n is None:
            self.entity_df.loc[self.entity_df['type'] == 'fractures', 'active'] = 1
        else:
            self.entity_df.loc[self.entity_df['type'] == 'fractures', 'active'] = 0
            if len(set_n) > 0:
                for n in set_n:
                    self.entity_df.loc[self.entity_df['f_set'] == n, 'active'] = 1

    def is_set_active(self, set_n: int) -> bool:
        """
        Method used to return if a given fracture set is active in the fracture network
        :param set_n: set to check
        :return: Bool value of the test
        """

        fractures = self._fractures_components

        value = fractures.loc[fractures['f_set'] == set_n, 'active'].values[0]

        return value

    #  ==================== Boundaries property ====================

    @property
    def boundaries(self) -> Boundary:
        """
        Property that returns a Boundary entity object of all the active boundary groups.
        :return: Boundary entity object
        """
        if self._active_boundaries_df is not None:
            return Boundary(self._active_boundaries_df)
        else:
            return None

    @property
    def _boundaries_components(self) -> DataFrame:
        """
        Internal property that returns the boundary components of the Fracture network df.
        :return: Pandas dataframe slice of the boundary groups components
        """

        boundaries = self.entity_df.loc[self.entity_df['type'] == 'boundary']
        if not boundaries.empty:
            return boundaries
        else:
            return None

    @property
    def _active_boundaries_components(self) -> DataFrame:
        """
        Internal property that returns the active boundary group components in the of the Fracture network df
        :return: Pandas dataframe slice of active boundary group components
        """

        boundaries = self.entity_df.loc[self.entity_df['type'] == 'boundary']

        active_boundaries = boundaries.loc[boundaries['active'] == 1]

        if not active_boundaries.empty:

            return active_boundaries
        else:
            return None

    @property
    def _active_boundaries_df(self) -> GeoDataFrame:
        """
        Internal property that returns the dataframe of the active boundary
        :return: GeoPandas DataFrame of the active boundaries of the fracture network
        """

        df = GeoDataFrame()

        boundaries = self._active_boundaries_components

        if boundaries is not None:

            for row, fracture in boundaries.iterrows():
                df = pd.concat([df, fracture['object'].entity_df], ignore_index=True)

            return df
        else:
            return None

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

        boundary_groups = set(boundary.entity_df['b_group'])

        for group_n in boundary_groups:

            boundary_df = boundary.entity_df.loc[boundary.entity_df['b_group'] == group_n]
            boundary_group = Boundary(gdf=boundary_df, group_n=group_n)

            if group_n not in self._df['b_group'].values:

                new_df = DataFrame([['boundary', boundary_group, group_n, 1]],
                                   columns=['type', 'object', 'b_group', 'active'])
                self._df = pd.concat([self._df, new_df], ignore_index=True)
            else:
                self._df.loc[self._df['b_group'] == group_n, 'object'] = boundary_group

    def boundary_object(self, group_n: int) -> Boundary:
        """
        Method that returns the Node object of a given group_number
        :param group_n: Number of the group
        :return: Boundary object
        """

        return self._boundaries_components.loc[self._boundaries_components['b_group'] == group_n, 'object'].values[0]

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
                self.entity_df.loc[self.entity_df['b_group'] == n, 'active'] = 1

    def is_group_active(self, group_n: int) -> bool:
        """
        Method used to return if a given boundary group is active in the fracture network
        :param group_n: set to check
        :return: Bool value of the test
        """

        boundaries = self._boundaries_components
        value = boundaries.loc[boundaries['b_group'] == group_n, 'active'].values[0]

        return value

    #  ==================== Backbone methods ====================

    def calculate_backbone(self, biggest_region=True):
        """
        Calculate the backbone(s) of the network and add the calculated nodes to the network.

        :param biggest_region: Output only most connected region. Default is True
        """

        fractures = self.fractures

        connectivity = vtkConnectivityFilter()

        connectivity.AddInputData(fractures.vtk_object)
        # if biggest_region: # For now only biggest region
        connectivity.SetExtractionModeToLargestRegion()

        connectivity.Update()

        vtkbackbone = PolyData(connectivity.GetOutput())

        backbone_set_n = self.sets[-1] + 1 # use the last available set and add +1. This could be expanded for multiple backbones

        backbone = Backbone(set_n=backbone_set_n)
        backbone.vtk_object = vtkbackbone
        backbone.crs = self.crs

        new_df = DataFrame([['backbone', backbone, backbone_set_n, 0]],
                           columns=['type', 'object', 'f_set', 'active'])
        self._df = pd.concat([self._df, new_df], ignore_index=True)

    @property
    def backbone(self):
        """
        Property that returns a Fractures entity object of the backbone.
        :return: Fracture entity object
        """
        return self._df.loc[self._df['type'] == 'backbone', 'object'].values

    #  ==================== Generic methods ====================

    def fracture_network_to_components_df(self) -> DataFrame:

        """
        Method used to return the fracture network as a single geopandas dataframe.
        :return: Geopandas DataFrame of the whole fracture network
        """

        gdf = DataFrame()

        nodes = self._active_nodes_df

        gdf = pd.concat([gdf, nodes], ignore_index=True)

        fractures = self._active_fractures_df

        gdf = pd.concat([gdf, fractures], ignore_index=True)

        boundaries = self._active_boundaries_df

        gdf = pd.concat([gdf, boundaries], ignore_index=True)

        if 'n_type' in gdf.columns:
            gdf['n_type'] = gdf['n_type'].fillna(-9999).astype('int64')
        gdf['f_set'] = gdf['f_set'].fillna(-9999).astype('int64')
        gdf['censored'] = gdf['censored'].fillna(-9999).astype('int64')
        if 'b_group' in gdf.columns:
            gdf['b_group'] = gdf['b_group'].fillna(-9999).astype('int64')
        return gdf

    def vtk_object(self, include_nodes: bool = True) -> PolyData:

        """
        Method used to return a vtkPolyData representation of the fracture network
        :param include_nodes: Bool flag used to control if include or not the nodes in the fracture network object
        :return: vtkPolyData of the fracture network
        """

        vtk_obj = Rep.fracture_network_vtk_rep(self.fracture_network_to_components_df(), include_nodes=include_nodes)
        return vtk_obj

    def network_object(self) -> Graph:
        """
        Method used to return a networkx Graph representation of the fracture network
        :return: Graph of the fracture network
        """

        network_object = Rep.networkx_rep(self.vtk_object(include_nodes=False))
        return network_object

    def check_network(self, check_single=True, save_shp=None):
        """
        Method used to check if network-wide the geometries are correct i.e.:
        + No repeating points
        + No overlaps

        By default, the method will return a list of geometries that need to be fixed. Additionally, a shp file can be
        saved with only the geometries that need to be corrected.

        :param remove_dup: Automatically remove duplicate points. By default, True. When false, a point shapefile where double points are present will be saved
        :param check_single: Perform check also for the single components
        :param save_shp: Path to save the shp of the check. If check_single is true then also the results of the single component check will be saved.
        """

        df = self.fracture_network_to_components_df()
        df = df.loc[df['type'] != 'node']

        set_n = np.array(list(set(df['f_set'])))

        overlaps_list = []
        overlaps_list_dict = {s: [] for s in set_n[set_n>0]}
        overlaps_geometry_list = []
        intersections_list = []
        intersections_geometry_list = []

        for line, geom in enumerate(df.geometry):

            if df.loc[line, 'type'] == 'boundary':
                mask = np.ones(df.geometry.size, dtype=bool)
                mask[line] = False
                sub_df = df[mask]
                intersections = sub_df.intersects(geom)
                touching = sub_df.touches(geom)
                xor = intersections != touching
                if xor.any():
                    filtered_df = sub_df[xor]
                    for n in set(filtered_df['f_set']):
                        int_dict = dict()
                        int_dict['boundary_int'] = list(filtered_df.loc[filtered_df['f_set'] == n, 'og_line_id'].values)
                        overlaps_list_dict[n].append(int_dict)
                    intersections_list = filtered_df['og_line_id'].values
                    intersections_geometry_list = filtered_df['geometry'].values

            else:
                overlaps = df.overlaps(geom)
                if overlaps.any():
                    overlaps_list.append(df.loc[line, 'og_line_id'])
                    overlaps_geometry_list.append(df.loc[line, 'geometry'])
                    set_n = df.loc[line, 'f_set']
                    overlaps_list_dict[set_n].append(df.loc[line, 'og_line_id'])

        if save_shp:
            path_frac = os.path.join(save_shp, 'frac_corr.shp')

            f_out_dict = {'og_id': [*overlaps_list, *intersections_list],
                          'geometry': [*overlaps_geometry_list, *intersections_geometry_list]}

            out_df = GeoDataFrame(f_out_dict, crs=self.crs)
            out_df.to_file(path_frac)

        else:
            print(overlaps_list_dict)

    def clean_network(self, buffer = 0.05, inplace=True, only_boundary=False):
        """Tidy the intersection of the active entities in the fracture network. A buffer is applied to all the
        geometries to ensure intersection in a given radius.

        :param only_boundary: Apply cleaning only on the fractures intersecting the boundary
        :param buffer: Applied buffer to the geometries of the entity.
        :param inplace: If true automatically replace the network with the clean one, if false then return the clean
         geopandas dataframe. Default is True
         """

        if inplace:
            if only_boundary:
                Geometry.tidy_intersections_boundary_only(self)
            else:
                Geometry.tidy_intersections(self)
        else:
            if only_boundary:
                Geometry.tidy_intersections_boundary_only(self, inplace=False)
            else:
                Geometry.tidy_intersections(self, inplace=False)

    def calculate_topology(self, clean_network=True, only_boundary=False):
        """
        Calculate the topology of the network and add the calculated nodes to the network.

        :param clean_network: If true, before calculating the topology the network is cleaned with the clean_network. Default is True
        :param only_boundary: Apply cleaning only on the fractures intersecting the boundary
        """
        if clean_network is True:
            self.clean_network(only_boundary=only_boundary)

        nodes_dict, origin_dict = Topology.nodes_conn(self)
        self.add_nodes_from_dict(nodes_dict,origin_dict=origin_dict, classes=None)






    @property
    def fraction_censored(self) -> float:
        """Get the fraction of censored fractures in the network """

        n_censored = self.fractures.entity_df['censored'] == 1

        total = self.fractures.entity_df['censored'] >= 0

        return len(self.fractures.entity_df[n_censored])/len(self.fractures.entity_df[total])

    #  ==================== Plotting methods ====================

    def vtk_plot(self,
                 markersize=5,
                 fracture_linewidth=1,
                 boundary_linewidth=1,
                 fracture_color='black',
                 boundary_color='red',
                 color_set=False,
                 show_plot=True,
                 return_plot=False,
                 notebook=True):
        """
        Method used to plot the fracture network using vtk
        :param markersize:
        :param fracture_linewidth:
        :param boundary_linewidth:
        :param fracture_color:
        :param boundary_color:
        :param color_set:
        :param show_plot:
        :param return_plot:
        :return:
        """

        plts.vtkplot_frac_net(self,
                              markersize=markersize,
                              fracture_linewidth=fracture_linewidth,
                              boundary_linewidth=boundary_linewidth,
                              fracture_color=fracture_color,
                              boundary_color=boundary_color,
                              color_set=color_set,
                              show_plot=show_plot,
                              return_plot=return_plot,
                              notebook=notebook)

    def backbone_plot(self,
                      method='vtk',
                      fracture_linewidth=1,
                      boundary_linewidth=1,
                      fracture_color='black',
                      boundary_color='red',
                      return_plot=False,
                      show_plot=True,
                      notebook=True):
        """
        Method used to plot the fracture network using vtk
        :return:
        """
        if method == 'vtk':
            plts.vtkplot_backbone(self,
                                  fracture_linewidth=fracture_linewidth,
                                  boundary_linewidth=boundary_linewidth,
                                  fracture_color=fracture_color,
                                  boundary_color=boundary_color,
                                  return_plot=return_plot,
                                  show_plot=show_plot,
                                  notebook=notebook)
        elif method == 'matplot':
            plts.matplot_backbone(self,
                                  fracture_linewidth,
                                  boundary_linewidth,
                                  fracture_color,
                                  boundary_color,
                                  return_plot,
                                  show_plot)

    def mat_plot(self,
                 markersize=5,
                 fracture_linewidth=1,
                 boundary_linewidth=1,
                 fracture_color='black',
                 boundary_color='red',
                 color_set=False,
                 show_plot=True,
                 return_plot=False):
        """
        Method used to plot the fracture network using matplotlib
        :param markersize:
        :param fracture_linewidth:
        :param boundary_linewidth:
        :param fracture_color:
        :param boundary_color:
        :param color_set:
        :param show_plot:
        :param return_plot:
        :return:
        """
        plts.matplot_frac_net(self,
                              markersize,
                              fracture_linewidth,
                              boundary_linewidth,
                              fracture_color,
                              boundary_color,
                              color_set,
                              show_plot,
                              return_plot)

    def ternary_plot(self):
        """
        Method used to plot the ternary diagram of the fracture network
        :return:
        """
        plts.matplot_ternary(self)

    #  ==================== Output methods ====================

    def save_csv(self, path: str, sep: str = ',', index: bool = False):
        """
        Save the fracture network entity df as csv
        :param index:
        :type sep: object
        :param path:
        :return:
        """

        if self.nodes is not None:
            self.nodes.save_csv(path)

        if self.fractures is not None:
            self.fractures.save_csv(path)

        if self.boundaries is not None:
            self.boundaries.save_csv(path)

        if self.backbone is not None:
            for bb in self.backbone:
                bb.save_csv(path)

    def save_shp(self, path: str):
        """
        Save the entity df as shp
        :param path:
        :return:
        """

        if self.nodes is not None:
            self.nodes.save_shp(path)

        if self.fractures is not None:
            self.fractures.save_shp(path)

        if self.boundaries is not None:
            self.boundaries.save_shp(path)

        if self.backbone is not None:
            for bb in self.backbone:
                bb.save_shp(path)