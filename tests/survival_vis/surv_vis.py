import numpy as np
import scipy.stats as ss
import shapely as shp
import geopandas as gpd
import pyvista as pv
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
import matplotlib.pyplot as plt

outer_bounds = [[0, 0, 0],
                [10, 0, 0],
                [10, 10, 0],
                [0, 10, 0],
                [0, 0, 0]]

inner_bounds = [(2.5, 2.5, 0), (7.5, 2.5, 0), (2.5, 7.5, 0), (7.5, 7.5, 0)]


centers = np.array([np.random.uniform(2.5, 7.5, size=100),
                   np.random.uniform(2.5, 7.5, size=100),
                   np.zeros(100)]).T.reshape(-1, 3)


line_appender = vtkAppendPolyData()

distr = ss.norm(0, 1)

random_lengths = np.random.normal(*distr.args, size=100)

pdf = distr.pdf(np.sort(random_lengths))

plt.plot(pdf)
plt.show()


for center, random_length in zip(centers, random_lengths):

    vertex1 = center.copy()
    vertex1[0] -= random_length

    vertex2 = center.copy()
    vertex2[0] += random_length

    line = pv.lines_from_points([vertex1, vertex2])
    line['length'] = random_length
    line_appender.AddInputData(line)

line_appender.Update()

outer_bounds_pv = pv.lines_from_points(outer_bounds)
centers_pv = pv.PolyData(centers)

plotter = pv.Plotter()
plotter.add_mesh(outer_bounds_pv)
plotter.add_mesh(line_appender.GetOutput())
plotter.view_xy()

plotter.add_camera_orientation_widget()
plotter.show()