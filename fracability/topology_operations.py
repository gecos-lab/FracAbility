from vtkmodules.vtkFiltersCore import vtkConnectivityFilter

from fracability.Entities import FractureNetwork, Nodes

from pyvista import PolyData


def nodes_conn(obj: FractureNetwork, inplace=True):

    adj_dict = obj.network_object.adj
    frac_net = obj.vtk_object

    fracture_nodes = Nodes()

    extr_nodes = frac_net.extract_points(frac_net.point_data['type'] == 'fracture', include_cells=False)

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

    n_nodes = extr_nodes.n_points
    for node in extr_nodes['vtkOriginalPointIds']:  # For each node of the fractures:
        print(f'Classifying node {node} of {n_nodes} ', end='\r')

        n_edges = len(adj_dict[node].keys())  # Calculate number of connected nodes

        if n_edges == 2:  # Discriminate V and internal nodes
            cells = frac_net.extract_points(node)  # Extract the cells
            if len(set(cells['RegionId'])) == 1:  # Check if the cellid changes
                n_edges = -9999  # Classify internal nodes

        elif n_edges == 3:  # Discriminate Y and U nodes
            cells = frac_net.extract_points(node)
            if 'boundary' in cells.cell_data['type']:
                n_edges = 5

        elif n_edges > 4:
            n_edges = -9999

        class_list.append(n_edges)  # Append the value (number of connected nodes)
    class_names = [class_dict[i] for i in class_list]

    extr_nodes['class_id'] = class_list

    extr_nodes['class_names'] = class_names
    extr_nodes = extr_nodes.extract_points(extr_nodes['class_id'] >= 0)

    fracture_nodes.vtk_object = extr_nodes
    obj.nodes = fracture_nodes


def find_backbone(obj: FractureNetwork) -> PolyData:

    fractures = obj.fractures.vtk_object

    connectivity = vtkConnectivityFilter()

    connectivity.AddInputData(fractures)
    connectivity.SetExtractionModeToLargestRegion()
    connectivity.Update()

    backbone = PolyData(connectivity.GetOutput())

    return backbone
