from abc import ABC, abstractmethod

import geopandas
import networkx
from pyvista import PolyData
from vtkmodules.vtkFiltersCore import vtkCleanPolyData

from fracability.Representations import NetworkxRepr
from fracability.utils.shp_operations import int_node
import numpy as np


class Operations(ABC):
    """
    Generic class to group different topological operations that can be applied
    to the BaseEntities
    """

    def __init__(self):
        self.input_object = None
        self.output_obj = None

    @abstractmethod
    def set_input(self, op_obj):
        """
        Set the input data
        :param op_obj: Operation object
        :return:
        """

    def get_output(self):
        """ Return the output of the given operation"""
        return self.output_obj


class Cleaner(Operations):
    """
    Cleaner class used to clean Fracture Network objects
    """
    def set_input(self, obj):
        self.input_object = obj

    def tidy_intersections(self, buffer=0.05):
        """
                Tidy intersections. For this function to properly work it is advised also to
                center the dataframe to avoid rounding errors. A buffer is applied to be sure that
                lines touch.
                :param op_object: Object that the operation applies to
                :param buffer: Buffer value applied to the network
                """
        df_buffer = self.input_object.buffer(buffer)
        for idx_line1, line in self.input_object.iterrows():
            line1 = line['geometry']
            df_buffer.drop(index=idx_line1, inplace=True)  # Remove the geometry to avoid self intersection

            idx_list = df_buffer.index[df_buffer.intersects(line1) == True]  # Subset the intersecting lines

            intersections = self.input_object.loc[idx_list]

            for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:

                new_geom = int_node(line1, line2, [idx_line1, idx_line2])  # Calculate and add the intersection node.

                for key, value in new_geom.items():
                    self.input_object.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry

                line1 = self.input_object.loc[
                    idx_line1, 'geometry']  # Use as the reference line (in the int_node function) the new geometry.

    def get_output(self):
        return self.input_object


class NetworkXGraph(Operations):
    """
    Class used to work on the fracture networkx topology graph
    """
    def __init__(self):
        super().__init__()
        self.adj_dict = None
        self.class_list = []
        self.class_names = []

    def set_input(self, network: NetworkxRepr):
        self.input_object = network

    def nodes_conn(self):
        """
        Create an ordered list of number of connection per node. Each value in the list
        represents the number of connection for the point n in the vtk dataset
        :return:
        """
        self.adj_dict = self.input_object.get_repr().adj
        network = self.input_object.get_vtk_repr()
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
        for i, node in enumerate(self.adj_dict):  # For each node in the dict:
            print(f'Classifying {i}/{n_nodes} nodes', end='\r')

            n_edges = len(self.adj_dict[node].keys())  # Calculate number of connected nodes
            if n_edges == 2:  # Discriminate V and internal nodes
                cells = network.extract_points(node)  # Extract the cells
                if len(set(cells['RegionId'])) == 1:  # Check if the cellid changes
                    n_edges = -9999  # Classify internal nodes

            elif n_edges == 3:  # Discriminate Y and U nodes
                cells = network.extract_points(node)
                if 'boundary' in cells.cell_data['type']:
                    # print(cells.cell_data['type'])
                    net_index = cells.cell_data['RegionId'][np.where(cells.cell_data['type'] != 'boundary')[0]]
                    # self.df.loc[net_index, 'U-nodes'] = 1
                    n_edges = 5

            elif n_edges > 4:
                n_edges = -9999

            self.class_list.append(n_edges)  # Append the value (number of connected nodes)
        self.class_names = [class_dict[i] for i in self.class_list]