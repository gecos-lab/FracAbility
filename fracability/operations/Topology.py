from shapely.geometry import Point
import numpy as np


def nodes_conn(obj):

    """
    Define the topology of a network using networkx.degree. With this method also censored fractures are defined and
    node origin are calculated. By node origin we define which entities are related to the given node e.g.:
        + I node with node origin x -> related to a fracture of set x
        + Y node with node origin xy -> related to the intersection of fractures of set x and y
        + Y node with node origin x -> related to the intersection of fractures of the same set x
        + Y node with node origin xyz -> triple intersection, makes no sense -> problem in the geometry
        + X node with node origin xy -> related to the intersection of fractures of set x and y
        + X node with node origin wxyz -> quadruple intersection, makes no sense -> problem in the geometry

    :param obj: Fractures or FractureNetwork object
    :return: list of shapely geometry points, a list of corresponding node classes and a list of node origin
    """

    network_obj = obj.network_object()

    vtk_obj = obj.vtk_object(include_nodes=False)

    entity_df_obj = obj.fracture_network_to_components_df()

    fractures_vtk_obj = obj.fractures.vtk_object

    frac_idx = np.where(vtk_obj.point_data['type'] == 'fracture')[0]

    node_dict = {}
    tot_idx = len(frac_idx)
    print('\n\n')
    for node in frac_idx:  # For each node of the fractures:
        print(f'Analyzing nodes:{node+1}/{tot_idx}', end='\r')

        n_edges = network_obj.degree[node]  # Calculate number of connected nodes

        point = Point(vtk_obj.points[node])

        cells = fractures_vtk_obj.extract_points(node)
        if cells.number_of_cells == 0:
            node_origin = -9999
        else:
            node_origin = ''.join([str(int(c)) for c in set(cells['f_set'])])

        if n_edges == 2:  # Exclude internal and V nodes
            n_edges = -9999

        elif n_edges == 3:  # Discriminate Y (3 or 6) and U (5) nodes

            cells = vtk_obj.extract_points(node)

            if 'boundary' in cells['type']:

                n_edges = 5
                index = vtk_obj.point_data['RegionId'][node]
                entity_df_obj.loc[index, 'censored'] = 1

            else:
                if len(node_origin) > 1:  # Discriminate between Y nodes between different sets (3) or same set (6)
                    n_edges = 6
                else:
                    n_edges = 3

        elif n_edges == 4:
            cells = vtk_obj.extract_points(node)
            if 'boundary' in cells['type']:
                n_edges = 5
                index = vtk_obj.point_data['RegionId'][node]
                entity_df_obj.loc[index, 'censored'] = 1
            else:
                n_edges = 4

        elif n_edges > 4:

            n_edges = -9999

        node_dict[point] = (n_edges, node_origin)

    obj.entity_df = entity_df_obj
    print('\n\nDone!')
    return node_dict


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
