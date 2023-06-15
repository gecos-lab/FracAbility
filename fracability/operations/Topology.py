from copy import deepcopy

from matplotlib import pyplot as plt
from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

from fracability.Entities import BaseEntity, FractureNetwork, Nodes

from shapely.geometry import Point, MultiPoint
from geopandas import GeoDataFrame
from pyvista import PolyData
import numpy as np


def nodes_conn(obj: BaseEntity, inplace=True):

    network = obj.network_object
    vtk_obj = obj.vtk_object

    frac_idx = np.where(vtk_obj.point_data['type'] == 'fracture')[0]

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

    # n_nodes = vtk_obj.n_points
    node_geometry = []
    for node in frac_idx:  # For each node of the fractures:
        print(f'Classifying node {node} of {len(frac_idx)} ', end='\r')

        n_edges = network.degree[node]  # Calculate number of connected nodes

        point = Point(vtk_obj.points[node])

        if n_edges == 2:  # Remove internal and V nodes
            n_edges = -9999
        elif n_edges == 3:  # Discriminate Y and U nodes
            cells = vtk_obj.extract_points(node)
            if 'boundary' in cells.cell_data['type']:
                n_edges = 5
                index = vtk_obj['RegionId'][node]
                obj.entity_df.loc[index, 'censored'] = 1
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

    entity_df = GeoDataFrame({'type': 'node', 'node_type': class_list, 'geometry': node_geometry},
                             crs=obj.entity_df.crs)
    fracture_nodes = Nodes(entity_df)

    return fracture_nodes


def find_backbone(obj: FractureNetwork) -> PolyData:

    fractures = obj.fractures.vtk_object

    connectivity = vtkConnectivityFilter()

    connectivity.AddInputData(fractures)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()

    backbone = PolyData(connectivity.GetOutput())

    return backbone
