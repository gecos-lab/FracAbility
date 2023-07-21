
from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

from fracability.Entities import FractureNetwork, Nodes


from shapely.geometry import Point
from geopandas import GeoDataFrame
import numpy as np


def nodes_conn(obj: FractureNetwork, inplace=True):

    network_obj = obj.network_object
    vtk_obj = obj.vtk_object(include_nodes=False)
    entity_df_obj = obj.fracture_network_to_components_df()

    fractures_vtk_obj = obj.fractures.vtk_object

    frac_idx = np.where(vtk_obj.point_data['type'] == 'fracture')[0]

    n_nodes = vtk_obj.n_points
    class_list = []
    Y_node_origin = []

    node_geometry = []
    for node in frac_idx:  # For each node of the fractures:
        # print(f'Classifying node {node} of {len(frac_idx)} ', end='\r')

        n_edges = network_obj.degree[node]  # Calculate number of connected nodes

        point = Point(vtk_obj.points[node])

        cells = fractures_vtk_obj.extract_points(node)
        origin_list = ';'.join([str(int(c)) for c in set(cells['f_set'])])

        if n_edges == 2:  # Exclude internal and V nodes
            n_edges = -9999

        elif n_edges == 3:  # Discriminate Y and U nodes

            cells = vtk_obj.extract_points(node)

            if 'boundary' in cells['type']:

                n_edges = 5
                index = vtk_obj['RegionId'][node]
                entity_df_obj.loc[index, 'censored'] = 1

            else:
                if len(origin_list) > 1:
                    n_edges = 6
                else:
                    n_edges = 3

        elif n_edges > 4:
            n_edges = 4

        node_geometry.append(point)
        class_list.append(n_edges)  # Append the value (number of connected nodes)

        Y_node_origin.append(origin_list)

    obj.entity_df = entity_df_obj
    class_list = np.array(class_list)
    n_origin_array = np.array(Y_node_origin)
    node_geometry = np.array(node_geometry)

    classes = [1, 3, 4, 5, 6]

    for c in classes:

        node_index = np.where(class_list == c)[0]

        if node_index.any():

            node_geometry_set = node_geometry[node_index]
            class_list_set = class_list[node_index]
            n_origin_array_set = n_origin_array[node_index]

            entity_df = GeoDataFrame({'type': 'node', 'n_type': class_list_set, 'n_origin': n_origin_array_set,
                                      'geometry': node_geometry_set}, crs=entity_df_obj.crs)

            nodes = Nodes(gdf=entity_df, node_type=c)

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
