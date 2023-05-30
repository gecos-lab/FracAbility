
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.geometric_operations import center_object, tidy_intersections,calculate_seg_length
from fracability.clean_operations import clean_dup_points, connect_dots
from fracability.topology_operations import nodes_conn, find_backbone

n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'
# n_path = 'fracability/datasets/frac_pesce_nolen.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'

# n_path = '/home/gabriele/STORAGE/projects/Ntwrk/Betta_01_Fracture_mapping/Fracture_network_tot.shp'
# b_path = '/home/gabriele/STORAGE/projects/Ntwrk/Betta_01_Fracture_mapping/Interpretation_boundary_tot.shp'
frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fractures = Entities.Fractures(frac_gpd)
boundaries = Entities.Boundary(bound_gpd)

# clean_dup_points(fractures)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)


center_object(fracture_net)


tidy_intersections(fracture_net)
connect_dots(fracture_net)

# fracture_net.boundaries.vtk_object.plot()

backbone = find_backbone(fracture_net)

#
nodes_conn(fracture_net)

calculate_seg_length(fracture_net)

print(fracture_net.entity_df)
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
