from scipy import stats as ss
import pyvista as pv
import numpy as np
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
from vtkmodules.vtkFiltersModeling import vtkCookieCutter

from fracability import Entities
from fracability.operations.Geometry import tidy_intersections
from fracability.operations.Topology import nodes_conn

params = (1.004836094520663, 0, 2.9804836275787645)

xmin = 636956.8988181990571320
xmax = 637087.6015316098928452

mean_x = np.mean([xmax, xmin])


ymin = 4518449.8742292737588286
ymax = 4518609.1086281584575772

mean_y = np.mean([ymax, ymin])

scaled_xmin = xmin-mean_x
scaled_xmax = xmax-mean_x

scaled_ymin = ymin-mean_y
scaled_ymax = ymax-mean_y

theta = 34
n_fractures = 1600

distr = ss.lognorm(*params)

# print(distr.mean(), distr.std())

lengths = ss.lognorm.rvs(*params, n_fractures)

half_lengths = lengths/2

centers_x = np.random.uniform(scaled_xmin, scaled_xmax, n_fractures)
centers_y = np.random.uniform(scaled_ymin, scaled_ymax, n_fractures)


x1 = centers_x+half_lengths*np.cos(np.deg2rad(theta))
x2 = centers_x+half_lengths*np.cos(np.deg2rad((theta+180) % 360))

y1 = centers_y+half_lengths*np.sin(np.deg2rad(theta))
y2 = centers_y+half_lengths*np.sin(np.deg2rad((theta+180) % 360))


xy1 = np.vstack((x1, y1)).T

xy2 = np.vstack((x2, y2)).T


xy1 = np.insert(xy1, range(1, n_fractures+1, 1), [0, 0], axis=0)
xy2 = np.insert(xy2, range(0, n_fractures, 1), [0, 0], axis=0)

complete = xy1+xy2

xyz = np.hstack((complete, np.zeros((len(complete), 1))))

conn = np.insert(np.arange(0, len(xyz)), np.arange(0, len(xyz), 2), 2)

lines = pv.PolyData(xyz, lines=conn)

lines['length'] = lengths
lines['RegionId'] = np.arange(0, n_fractures)


bounds_center = np.mean(xyz, axis=0)

origin = np.array([scaled_xmin, scaled_ymin, 0])

bounds_r = np.linalg.norm(bounds_center-origin)*0.7

print(bounds_r)

circle_x = np.linspace(bounds_center[0]-bounds_r, bounds_center[0]+bounds_r, 10000)
circle_y = np.sqrt(bounds_r**2-(circle_x-bounds_center[0])**2) + bounds_center[1]
circle_y2 = -np.sqrt(bounds_r**2-(circle_x[::-1][1:-1]-bounds_center[0])**2) + bounds_center[1]

circle_xy1 = np.vstack((circle_x, circle_y)).T
circle_xy2 = np.vstack((circle_x[::-1][1:-1], circle_y2)).T

circle_xy = np.append(circle_xy1, circle_xy2, axis=0)


circle_xy = np.append(circle_xy, [circle_xy1[0, :]], axis=0)

circle_xyz = np.hstack((circle_xy, np.zeros((len(circle_xy), 1))))

conn = np.insert(np.arange(0, len(circle_xy)-1), 0, len(circle_xy)-1)

window = pv.PolyData(circle_xyz, faces=conn)

# window.plot()

#
window['RegionId'] = [0]

cookie = vtkCookieCutter()

cookie.SetLoopsData(window)
cookie.SetInputData(lines)
cookie.SetPointInterpolationToLoopEdges()
cookie.Update()

fractures_cut = pv.PolyData(cookie.GetOutput())



# appender = vtkAppendPolyData()
# for i, scale in enumerate(np.arange(0.1, 1.1, 0.1)[::-1]):
#     scaled_points = bounds_points*scale
#     bounds = pv.PolyData(scaled_points, lines=[5, 0, 1, 2, 3, 0])
#     bounds['RegionId'] = i
#     appender.AddInputData(bounds)
#
# appender.Update()
#
# boundaries = pv.PolyData(appender.GetOutput())


fractures_1 = Entities.Fractures(set_n=1)
boundary = Entities.Boundary(group_n=1)


fractures_1.vtk_object = fractures_cut
boundary.vtk_object = window
# print (boundary.entity_df)
# #
#
frac_net = Entities.FractureNetwork()

frac_net.add_fractures(fractures_1)

frac_net.add_boundaries(boundary)

tidy_intersections(frac_net)
#
nodes_conn(frac_net)

frac_net.vtkplot()

# plotter = pv.Plotter()
#
# plotter.add_points(bounds_center)
# plotter.add_mesh(fractures_cut, scalars='length')
# plotter.add_mesh(window)
# #
# plotter.set_background('gray')
# plotter.view_xy()
# plotter.add_camera_orientation_widget()
# plotter.show()

