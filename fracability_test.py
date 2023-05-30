import geopandas
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
import pyvista as pv
import networkx as nx
from ast import literal_eval
import numpy as np
import shapely

from fracability import Entities
from fracability.geometric_operations import center_object, tidy_intersections, connect_dots
from fracability.topology_operations import nodes_conn

n_path = 'fracability/datasets/Fracture_network.shp'
b_path = 'fracability/datasets/Interpretation_boundary_laghettoSalza.shp'
# n_path = 'fracability/datasets/frac_pesce.shp'
# b_path = 'fracability/datasets/grid_pesce.shp'

# n_path = 'fracability/datasets/test_length.shp'

frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

# print(frac_gpd.crs)


fractures = Entities.Fractures(frac_gpd)
boundaries = Entities.Boundary(bound_gpd)

fracture_net = Entities.FractureNetwork()

fracture_net.add_fractures(fractures)
fracture_net.add_boundaries(boundaries)
# fracture_net.vtk_object.plot()
#

center_object(fracture_net)

tidy_intersections(fracture_net)

connect_dots(fracture_net)


nodes_conn(fracture_net)

# print(fracture_net.fractures.vtk_conn_object.array_names)

#
nodes = fracture_net.nodes.vtk_object



# print(nodes.points)
# print(fracture_net.vtk_object.points)
# vtk_test = fractures.get_vtk_output()
#
# calculate_seg_length(vtk_test)
#
#
#
#
# # tidy_frac_net = Entities.FractureNetwork(tidy_gdf)
# #
# # print(tidy_frac_net.fractures)
#
# graph = fracture_net.get_network_output()
# class_id, class_names = nodes_conn(graph, fracture_net)
#
# #
# # #
# fractures_nodes = fracture_net.get_nodes()
#
# fractures_nodes['class_id'] = class_id
# #
nodes = nodes.extract_points(nodes['class_id'] >= 0)
nodes.set_active_scalars('class_id')
#
#
plotter = pv.Plotter()
#
plotter.add_mesh(fracture_net.vtk_object, color='white')
# plotter.add_mesh(fracture_net.boundaries.get_nodes(), render_points_as_spheres=True, point_size=10,color='blue')
# plotter.add_mesh(fracture_net.fractures.get_nodes(), render_points_as_spheres=True, point_size=10,color='yellow')
plotter.add_mesh(nodes, render_points_as_spheres=True, point_size=10)
plotter.view_xy()
plotter.show()
