
import geopandas as gpd

import pyvista as pv


from fracability import Entities
from fracability.geometric_operations import center_object, tidy_intersections, connect_dots
from fracability.topology_operations import nodes_conn

n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'
# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'


frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fractures = Entities.Fractures(frac_gpd)
boundaries = Entities.Boundary(bound_gpd)


fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)


center_object(fracture_net)

tidy_intersections(fracture_net)

connect_dots(fracture_net)

nodes_conn(fracture_net)


nodes = fracture_net.nodes.vtk_object

nodes.set_active_scalars('class_id')

plotter = pv.Plotter()

plotter.add_mesh(fracture_net.vtk_object, color='white')
plotter.add_mesh(nodes, render_points_as_spheres=True, point_size=10)
plotter.view_xy()
plotter.show()
