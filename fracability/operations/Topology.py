from shapely.geometry import Point
import numpy as np
from itertools import chain
from pyvista import PolyData


def nodes_conn(obj):

    """
    Define the topology of a network using networkx.degree. With this method also censored fractures are defined and
    node origin are calculated. By node origin we define which entities are related to the given node e.g.:
        + I node with node origin [x] -> related to a fracture of set x
        + Y node with node origin [x, y] -> related to a fracture of set x abutting on a fracture of set y
        + Y node with node origin [x, x] -> related to the intersection of fractures of the same set x
        + U node with node origin [x, b] -> related to a fracture of set x intersecting the boundary (b)
        + Y node with node origin [x, y, z] -> triple intersection, makes no sense -> problem in the geometry
        + X node with node origin [x, y] -> related to the intersection of fractures of set x and y
        + X node with node origin [w, x, y, z] -> quadruple intersection, makes no sense -> problem in the geometry

    :param obj: Fractures or FractureNetwork object
    :return: list of shapely geometry points, a list of corresponding node classes and a list of node origin
    """

    fractures_vtk = obj.fractures.vtk_object
    boundary_vtk = obj.boundaries.vtk_object
    entity_df_obj = obj.fracture_network_to_components_df()
    point_dict = dict()
    origin_dict = dict()
    ids = []

    # to get all the nodes we append the start and end of a line (I nodes) and then the entire point_id list
    for i, cell in enumerate(fractures_vtk.cell):
        cell_ids = cell.point_ids
        ids.append([cell_ids[0]])
        ids.append([cell_ids[-1]])
        ids.append(cell_ids)

    # we then create a flattened list of the indexes
    ids = list(chain.from_iterable(ids))

    # and get the unique values that repeat more than once.
    # i.e. I nodes and all the nodes that repeat because of intersection with the fractures
    u, c = np.unique(ids, return_counts=True)

    ids = u[c > 1]

    # To define boundary intersection we search for overlapping points (with a decimal precision of e-5).
    # This method has a bit of a problem because vtk and shapely do not have the same precision and thus when comparing
    # points after the e-5 values are different
    fracture_points = fractures_vtk.points
    boundary_points = boundary_vtk.points

    boundary_common = np.isin(np.round(fracture_points, 5), np.round(boundary_points, 5)).all(axis=1)
    boundary_index = np.where(boundary_common == 1)[0]

    # After we explode the fractures_vtk to get all the segments of each line
    fractures_segm = fractures_vtk.extract_all_edges(use_all_points=True)

    # We then loop for each node id that we found at the start
    for i in ids:
        # this indicates the degree of the node (i.e. I, Y or X)
        neigh = fracture_points[fractures_segm.point_neighbors(i)]

        # these will be the cells id that contain the given node idx
        cells = fractures_vtk.point_cell_ids(i)

        # To get the node origin we find the unique values of the fracture set at the given node idx and sort
        # using argsort to get the order that we want (i.e. increasing frequency)
        sets = fractures_segm['f_set'][fractures_segm.point_cell_ids(i)]
        u_sets, f_sets = np.unique(sets, return_counts=True)
        sorting_index = np.argsort(f_sets)

        if len(cells) >= 3:
            print(f'\n\nInvalid point for lines: {fractures_vtk["og_line_id"][cells]} '
                  f'\n\nsets: {fractures_vtk["f_set"][cells]}, \n\nThe node will be classified accordingly'
                  f' to the number of intersection however, the intersection must be checked!')

        if len(neigh) != 2:
            point = Point(fracture_points[i])
            point_dict[point] = [len(neigh), i]
            origin_dict[point] = f'{u_sets[sorting_index]}'

    for i in boundary_index:
        point = Point(fracture_points[i])
        f_cells = fractures_vtk.point_cell_ids(i)
        origin_set = f'{fractures_vtk["f_set"][f_cells][0]}'

        point_dict[point] = [5, i]
        origin_dict[point] = f'{[origin_set, "b"]}'

    censored_lines = [fractures_vtk.point_cell_ids(idx)[0] for idx in boundary_index]
    entity_df_obj.loc[censored_lines, 'censored'] = 1
    obj.entity_df = entity_df_obj
    #fracture_nodes = PolyData(fractures_vtk.points)
    #fracture_nodes['topology'] = fractures_vtk['topology']

    # network_obj = obj.network_object()
    #
    # vtk_obj = obj.vtk_object(include_nodes=False)
    #
    # entity_df_obj = obj.fracture_network_to_components_df()
    #
    # fractures_vtk_obj = obj.fractures.vtk_object
    #
    # frac_idx = np.where(vtk_obj.point_data['type'] == 'fracture')[0]
    #
    # node_dict = {}
    # tot_idx = len(frac_idx)
    # print('\n\n')
    # for node in frac_idx:  # For each node of the fractures:
    #     print(f'Analyzing nodes:{node+1}/{tot_idx}', end='\r')
    #
    #     n_edges = network_obj.degree[node]  # Calculate number of connected nodes
    #
    #     point = Point(vtk_obj.points[node])
    #
    #     cells = fractures_vtk_obj.extract_points(node)
    #     if cells.number_of_cells == 0:
    #         node_origin = -9999
    #     else:
    #         node_origin = ''.join([str(int(c)) for c in set(cells['f_set'])])
    #
    #     if n_edges == 2:  # Exclude internal and V nodes
    #         n_edges = -9999
    #
    #     elif n_edges == 3:  # Discriminate Y (3 or 6) and U (5) nodes
    #
    #         cells = vtk_obj.extract_points(node)
    #
    #         if 'boundary' in cells['type']:
    #
    #             n_edges = 5
    #             index = vtk_obj.point_data['RegionId'][node]
    #             entity_df_obj.loc[index, 'censored'] = 1
    #
    #         else:
    #             if len(node_origin) > 1:  # Discriminate between Y nodes between different sets (3) or same set (6)
    #                 n_edges = 6
    #             else:
    #                 n_edges = 3
    #
    #     elif n_edges == 4:
    #         cells = vtk_obj.extract_points(node)
    #         if 'boundary' in cells['type']:
    #             n_edges = 5
    #             index = vtk_obj.point_data['RegionId'][node]
    #             entity_df_obj.loc[index, 'censored'] = 1
    #         else:
    #             n_edges = 4
    #
    #     elif n_edges > 4:
    #
    #         n_edges = -9999
    #
    #     node_dict[point] = (n_edges, node_origin)
    #
    # obj.entity_df = entity_df_obj
    # print('\n\nDone!')
    return point_dict, origin_dict


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
