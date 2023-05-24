import vtk
import pyvista as pv
from fracability import Entities
from fracability import Operations
from fracability import Representations

import geopandas as gpd

n_path = '/home/gabriele/STORAGE/projects/FracAbility_test/fracability/datasets/Fracture_network_test.shp'
b_path = '/home/gabriele/STORAGE/projects/FracAbility_test/fracability/datasets/Interpretation_boundary_laghettoSalza.shp'


frac_gpd = gpd.read_file(n_path)
bound_gpd = gpd.read_file(b_path)

vtk_repr = Representations.VTKRepr()
net_repr = Representations.NetworkxRepr()

fractures = Entities.Fractures(frac_gpd)
boundary = Entities.Boundary(bound_gpd)

frac_net = Entities.FractureNetwork()
frac_net.add_fractures(fractures)
frac_net.add_boundaries(boundary)

frac_net.center_object()

shp_clean = Operations.Cleaner()
shp_clean.set_input(frac_net.df)

shp_clean.tidy_intersections(buffer=0.05)

frac_tidy_df = shp_clean.get_output()

vtk_repr.set_input(frac_tidy_df)

frac_net_vtk = frac_net.get_output(vtk_repr)
net_repr.set_input(frac_net_vtk)


test = Operations.NetworkXGraph()
test.set_input(net_repr)

test.nodes_conn()

points = pv.PolyData(frac_net_vtk.points)

points['test'] = test.class_names

points_filt = points.extract_points(points['test'] != 'Nan')
cmap_dict = {
    'I': 'Blue',
    'V': 'Green',
    'Y': 'Red',
    'X': 'Yellow',
    'U': 'Gray'
}

plotter = pv.Plotter()

plotter.add_mesh(frac_net_vtk)
plotter.add_mesh(points_filt,cmap=cmap_dict)
plotter.show()


#
# frac_net.tidy()
# frac_net.vtk_repr()
# plotter = pv.Plotter()
#
# plotter.add_mesh(frac_net.vtk_repr(), scalars='type')
# plotter.show()
# frac_net.calculate_graph()
# #
# nodes = frac_net.classify()
#
#
# sargs = dict(interactive=False,
#              vertical=False,
#              height=0.1,
#              title_font_size=16,
#              label_font_size=14)
#
# cmap_dict = {
#     'I': 'Blue',
#     'V': 'Green',
#     'Y': 'Red',
#     'X': 'Yellow',
#     'U': 'Gray'
# }
#
# cmap_dict_lines = {
#     'network': 'White',
#     'boundary': 'Black'
# }
#
# used_tags = list(set(nodes['class_tags']))
# used_tags.sort()
# cmap = [cmap_dict[i] for i in used_tags]
#
# plotter = pv.Plotter()
#
# plotter.add_mesh(frac_net.vtk_repr(),
#                  scalars='type',
#                  line_width=1,
#                  show_scalar_bar=False,
#                  cmap=['Red', 'White'])
# plotter.add_mesh(nodes,scalars='class_tags',
#                  render_points_as_spheres=True,
#                  point_size=7,
#                  show_scalar_bar=True,
#                  scalar_bar_args=sargs,
#                  cmap=cmap)
#
# plotter.show()
# frac_net.center_network()
#
# print(frac_net.df)
# print(frac_net.old_df)
#
#
#
# frac_net.vtk_repr().plot()
# frac_net_vtk = frac_net.get_vtk_repr()
# frac_net_vtk.plot()
# boundary_vtk = boundary.get_vtk_repr()
#
# boundary_vtk.plot()
# fig = plt.figure()
# ax = fig.add_subplot(111)
# frac_net.get_df().plot(ax=ax, label='network')
# boundary.get_df().plot(ax=ax, label='boundary',color='k')
# plt.legend()
# plt.show()
#
# plotter = pv.Plotter()
# plotter.add_mesh(frac_net_vtk)
# plotter.add_mesh(boundary)
#
# plotter.show()
