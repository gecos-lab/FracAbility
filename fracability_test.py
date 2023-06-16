
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections
from fracability.operations.Topology import nodes_conn
import fracability.Plotters as plotters

from fracability.operations.Statistics import NetworkFitter


# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'
#
# n1_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_1.shp'
# n2_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_2.shp'
#
n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'


fracs = gpd.read_file(n_path)

bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fractures = Entities.Fractures(fracs)

boundaries = Entities.Boundary(bound_gpd)

# clean_dup_points(fractures)

fracture_net = Entities.FractureNetwork()


fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)
# print(fracture_net.vtk_object.plot())


center_object(fracture_net)


tidy_intersections(fracture_net)


nodes = nodes_conn(fracture_net)

print(nodes.node_count)

fracture_net.add_nodes(nodes)

plotters.matplot_ternary(fracture_net)

