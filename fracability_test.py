
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.operations.Geometry import center_object, tidy_intersections,calculate_seg_length
from fracability.operations.Cleaners import connect_dots
from fracability.operations.Topology import nodes_conn, find_backbone

# n_path = 'fracability/datasets/Fracture_network.shp'
# b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'

n1_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_1.shp'
n2_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Set_2.shp'

b_path = '/home/gabriele/STORAGE/Unibro/Libri-e-dispense/Magistrale/Tesi/pz_pers/test_reti/attachments/Interpretation_boundary_laghettoSalza.shp'


fracs1_gpd = gpd.read_file(n1_path)
fracs2_gpd = gpd.read_file(n2_path)

bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fracture_s1 = Entities.Fractures(fracs1_gpd)
fracture_s2 = Entities.Fractures(fracs2_gpd)

boundaries = Entities.Boundary(bound_gpd)

# clean_dup_points(fractures)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fracture_s1)
fracture_net.add_fractures(fracture_s2)

fracture_net.add_boundaries(boundaries)


center_object(fracture_net)


tidy_intersections(fracture_net)
connect_dots(fracture_net)

# fracture_net.boundaries.vtk_object.plot()

backbone = find_backbone(fracture_net)

#
nodes_conn(fracture_net)

calculate_seg_length(fracture_net)


print(fracture_net.fractures.entity_df)
#
#
nodes = fracture_net.nodes.vtk_object
#
nodes.set_active_scalars('class_id')

plotter = pv.Plotter()

plotter.add_mesh(fracture_net.vtk_object, color='white')
plotter.add_mesh(nodes, render_points_as_spheres=True, point_size=10)
plotter.add_mesh(backbone, color='yellow')
plotter.view_xy()
plotter.show()
