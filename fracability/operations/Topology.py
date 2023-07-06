
from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

from fracability.Entities import BaseEntity, FractureNetwork, Nodes

from fracability.Adapters import frac_vtk_rep

from shapely.geometry import Point, MultiPoint
from geopandas import GeoDataFrame
from pyvista import PolyData
import numpy as np


def nodes_conn(obj: FractureNetwork, inplace=True):

    network_obj = obj.network_object
    vtk_obj = obj.vtk_object(include_nodes=False)
    entity_df_obj = obj.fracture_network_to_components_df()

    fractures_vtk_obj = frac_vtk_rep(entity_df_obj.loc[entity_df_obj['type'] == 'fracture'])

    frac_idx = np.where(vtk_obj.point_data['type'] == 'fracture')[0]

    class_list = []
    Y_node_origin = []

    # n_nodes = vtk_obj.n_points
    node_geometry = []
    for node in frac_idx:  # For each node of the fractures:
        # print(f'Classifying node {node} of {len(frac_idx)} ', end='\r')

        n_edges = network_obj.degree[node]  # Calculate number of connected nodes

        point = Point(vtk_obj.points[node])

        if n_edges == 2:  # Exclude internal and V nodes
            n_edges = -9999

        elif n_edges == 3:  # Discriminate Y and U nodes

            cells = vtk_obj.extract_points(node)

            if 'boundary' in cells.cell_data['type']:

                n_edges = 5
                index = vtk_obj['RegionId'][node]
                entity_df_obj.loc[index, 'censored'] = 1

            else:
                cells = fractures_vtk_obj.extract_points(node)
                tuple_set = tuple(set(cells.cell_data['set']))
                if len(tuple_set) > 1:
                    n_edges = 6
                else:
                    n_edges = 3
                Y_node_origin.append(tuple_set)

        elif n_edges > 4:
            n_edges = -9999

        node_geometry.append(point)
        class_list.append(n_edges)  # Append the value (number of connected nodes)

    obj.entity_df = entity_df_obj
    class_list = np.array(class_list)
    node_geometry = np.array(node_geometry)

    classes = [1, 3, 4, 5, 6]

    for c in classes:

        node_index = np.where(class_list == c)[0]

        if node_index.any():

            node_geometry_set = node_geometry[node_index]
            class_list_set = class_list[node_index]

            entity_df = GeoDataFrame({'type': 'node', 'node_type': class_list_set, 'Y_node_origin': None,
                                      'geometry': node_geometry_set}, crs=entity_df_obj.crs)

            nodes = Nodes(entity_df, c)

            obj.add_nodes(nodes)


# def find_backbone(obj: FractureNetwork) -> PolyData:
#
#     fractures = obj.fractures_components.vtk_object
#
#     connectivity = vtkConnectivityFilter()
#
#     connectivity.AddInputData(fractures)
#     connectivity.SetExtractionModeToLargestRegion()
#     connectivity.Update()
#
#     backbone = PolyData(connectivity.GetOutput())
#
#     return backbone
