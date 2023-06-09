from copy import deepcopy

from matplotlib import pyplot as plt
from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

from fracability.Entities import FractureNetwork, Nodes

from shapely.geometry import Point
from geopandas import GeoDataFrame
from pyvista import PolyData
import numpy as np


def nodes_conn(obj: FractureNetwork, inplace=True):

    frac_net = obj
    frac_net_df = frac_net.entity_df.copy()
    frac_net_vtk = frac_net.vtk_object
    fractures = frac_net.fractures
    fractures_vtk = fractures.vtk_object
    adj_dict = obj.network_object.adj

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

    n_nodes = fractures_vtk.n_points
    node_geometry = []
    for node in fractures_vtk['vtkOriginalPointIds']:  # For each node of the fractures:
        # print(f'Classifying node {node} of {n_nodes} ', end='\r')

        n_edges = len(adj_dict[node].keys())  # Calculate number of connected nodes

        point = Point(fractures_vtk.points[node])

        if n_edges == 2:  # Remove internal and V nodes
            n_edges = -9999
        elif n_edges == 3:  # Discriminate Y and U nodes
            cells = frac_net_vtk.extract_points(node)
            if 'boundary' in cells.cell_data['type']:
                n_edges = 5
                index = frac_net_vtk['RegionId'][node]
                frac_net_df.loc[index, 'censored'] = 1
        elif n_edges > 4:
            n_edges = -9999

        node_geometry.append(point)
        class_list.append(n_edges)  # Append the value (number of connected nodes)

    node_geometry = np.array(node_geometry)
    class_list = np.array(class_list)

    indexes = np.where(class_list >= 0)

    node_geometry = node_geometry[indexes]
    class_list = class_list[indexes]

    # class_names = [class_dict[i] for i in class_list]

    # fractures_vtk['class_id'] = class_list
    #
    # fractures_vtk['class_names'] = class_names
    # extr_nodes = fractures_vtk.extract_points(fractures_vtk['class_id'] >= 0, include_cells=False)

    entity_df = GeoDataFrame({'type': 'node', 'node_type': class_list, 'geometry': node_geometry},crs=frac_net_df.crs)
    fracture_nodes = Nodes(entity_df)

    if inplace:
        obj.entity_df = frac_net_df
        obj.add_nodes(fracture_nodes)
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = frac_net_df
        copy_obj.add_nodes(fracture_nodes)
        return copy_obj


def find_backbone(obj: FractureNetwork) -> PolyData:

    fractures = obj.fractures.vtk_object

    connectivity = vtkConnectivityFilter()

    connectivity.AddInputData(fractures)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()

    backbone = PolyData(connectivity.GetOutput())

    return backbone
