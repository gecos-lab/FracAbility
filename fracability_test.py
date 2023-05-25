
import geopandas as gpd
from matplotlib import pyplot as plt
import pyvista as pv

from fracability import Entities
from fracability.Operations import tidy_intersections, nodes_conn, isolate_intersections_boundary

n_path = 'fracability/datasets/frac_pesce.shp'
b_path = 'fracability/datasets/grid_pesce.shp'


frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

fractures = Entities.Fractures(frac_gpd)
boundaries = Entities.Boundary(bound_gpd)

tidy = tidy_intersections(fractures)


fracture_net = Entities.FractureNetwork()
#
fracture_net.add_fractures(tidy)
fracture_net.add_boundaries(boundaries)
#
fracture_net.center_object()
isolate_intersections_boundary(fracture_net)
fracture_net.get_vtk_output().plot()
# graph = fractures_tidy.get_network_output()
#
# class_id, class_names = nodes_conn(graph, fractures_tidy.get_vtk_output())
#
# fractures_tidy_nodes = fractures_tidy.get_nodes()
#
# fractures_tidy_nodes['class_id'] = class_id
#
# fractures_tidy_nodes = fractures_tidy_nodes.extract_points(fractures_tidy_nodes['class_id'] >= 0)
#
#
# plotter = pv.Plotter()
#
# plotter.add_mesh(fractures_tidy.get_vtk_output(),color='white')
# plotter.add_mesh(fractures_tidy_nodes)
# plotter.view_xy()
# plotter.show()