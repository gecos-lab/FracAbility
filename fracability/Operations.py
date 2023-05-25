from abc import ABC, abstractmethod

import geopandas
import matplotlib.pyplot as plt
import networkx
from pyvista import PolyData

from fracability.Entities import Fractures, Boundary, FractureNetwork
from fracability.utils.shp_operations import int_node
import numpy as np


def tidy_intersections(fractures: Fractures, buffer=0.05) -> Fractures:
    """
        Tidy intersections of the fracture network (without the boundary).
        For this function to properly work it is advised also to center the dataframe t
        o avoid rounding errors. A buffer is applied to be sure that lines touch.
        :param fractures: Input fracture entity object
        :param buffer: Buffer value applied to the network
    """

    gdf = fractures.entity_df
    df_buffer = gdf.buffer(buffer)
    for idx_line1, line in gdf.iterrows():
        line1 = line['geometry']

        idx_list = df_buffer.index[df_buffer.intersects(line1) == True]  # Subset the intersecting lines
        idx_list = idx_list[idx_list != idx_line1]  # Exclude the reference line index to avoid self intersection

        intersections = gdf.loc[idx_list]
        for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:

            new_geom = int_node(line1, line2, [idx_line1, idx_line2])  # Calculate and add the intersection node.

            for key, value in new_geom.items():
                gdf.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry

            line1 = gdf.loc[
                idx_line1, 'geometry']  # Use as the reference line (in the int_node function) the new geometry.
    return Fractures(gdf)


def isolate_intersections_boundary(frac_net: FractureNetwork, buffer = 0.05):
    """
        Tidy intersections of the fractures with the boundary.
        For this function to properly work it is advised also to center the dataframe t
        o avoid rounding errors. A buffer is applied to be sure that lines touch.
        :param frac_net: Input fracture network entity object
        :param buffer: Buffer value applied to the network
    """
    fractures_gdf = frac_net.entity_df.loc[frac_net.entity_df['type'] == 'fracture']
    boundary_gdf = frac_net.entity_df.loc[frac_net.entity_df['type'] == 'boundary']
    df_buffer = boundary_gdf.buffer(buffer)

    for line1 in df_buffer:

        idx_list = fractures_gdf.index[fractures_gdf.intersects(line1) == True]  # Subset the intersecting lines
        print(idx_list, len(idx_list))
    #     idx_list = idx_list[idx_list != idx_line1]  # Exclude the reference line index to avoid self intersection
    #
    #     intersections = fractures_gdf.loc[idx_list]
    #     for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:
    #
    #         new_geom = int_node(line1, line2, [idx_line1, idx_line2])  # Calculate and add the intersection node.
    #         print(new_geom)
    #         for key, value in new_geom.items():
    #             fractures_gdf.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry
    #
    # return fractures_gdf,boundary_gdf

def nodes_conn(graph: networkx.Graph, network: PolyData) -> list:
    """
    Create an ordered list of number of connection per node. Each value in the list
    represents the number of connection for the point n in the vtk dataset
    :return:
    """
    adj_dict = graph.adj
    class_list = []

    # Create a dict used to translate the numeric values with the classification
    class_dict = {
        1: 'I',
        2: 'V',
        3: 'Y',
        4: 'X',
        5: 'U',
        -9999: 'Nan'
    }

    n_nodes = network.n_points
    for i, node in enumerate(adj_dict):  # For each node in the dict:
        print(f'Classifying {i}/{n_nodes} nodes', end='\r')

        n_edges = len(adj_dict[node].keys())  # Calculate number of connected nodes

        if n_edges == 2:  # Discriminate V and internal nodes
            cells = network.extract_points(node)  # Extract the cells
            if len(set(cells['RegionId'])) == 1:  # Check if the cellid changes
                n_edges = -9999  # Classify internal nodes

        elif n_edges == 3:  # Discriminate Y and U nodes
            cells = network.extract_points(node)
            if 'boundary' in cells.cell_data['type']:
                # print(cells.cell_data['type'])
                # net_index = cells.cell_data['RegionId'][np.where(cells.cell_data['type'] != 'boundary')[0]]
                # self.df.loc[net_index, 'U-nodes'] = 1
                n_edges = 5

        elif n_edges > 4:
            n_edges = -9999

        class_list.append(n_edges)  # Append the value (number of connected nodes)
    class_names = [class_dict[i] for i in class_list]

    return class_list, class_names

