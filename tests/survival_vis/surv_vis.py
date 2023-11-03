import numpy as np
import scipy.stats as ss
import shapely as shp
import geopandas as gpd
import pyvista as pv
from vtkmodules.vtkFiltersCore import vtkAppendPolyData
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

x_min = 0
y_min = 0

x_max = 10
y_max = 10

bounds = np.array([[x_min, y_min, 0],
                   [x_min, y_max, 0],
                   [x_max, y_max, 0],
                   [x_max, y_min, 0]])

n_fractures = 30

res = 3

means = np.linspace(1, 5, res)
stds = np.linspace(1, 5, res)

centers = np.array([np.random.uniform(x_min, x_max, size=n_fractures),
                   np.random.uniform(y_min, y_max, size=n_fractures),
                   np.zeros(n_fractures)]).T.reshape(-1, 3)

mean_centers = np.mean(bounds, axis=0)

r = ((x_max-x_min)*np.sqrt(2))/2

disk = pv.Disc(mean_centers, inner=r, outer=r*0.995, c_res=100)

plotter = pv.Plotter(shape=(res, res))
plotter.background_color = 'gray'
plotter.add_camera_orientation_widget()
plotter.enable_image_style()

data_range = np.arange(0, 20, 0.01)

i = 1
for c, mean in enumerate(means):
    for i, std in enumerate(stds):
        # print(f'std:{std}')
        distr = ss.norm(mean, std)
        y = distr.sf(data_range)

        random_lengths = distr.rvs(n_fractures)/2

        vertex1 = centers.copy()
        vertex1[:, 0] -= random_lengths

        vertex2 = centers.copy()
        vertex2[:, 0] += random_lengths

        vertex1 = np.insert(vertex1, range(1, n_fractures+1, 1), [0, 0, 0], axis=0)
        vertex2 = np.insert(vertex2, range(0, n_fractures, 1), [0, 0, 0], axis=0)

        complete = vertex1+vertex2

        conn = np.insert(np.arange(0, len(complete)), np.arange(0, len(complete), 2), 2)
        lines = pv.PolyData(complete, lines=conn)

        plotter.subplot(c, i)
        plotter.add_mesh(lines)
        plotter.add_mesh(disk, color='r')
        plotter.view_xy()

#         plt.subplot(res, res, i)
#         plt.title(f'{mean}, {std}')
#         # plt.plot(mean_centers[0], mean_centers[1], 'o', markersize=500, markeredgecolor='r', mfc='none')
#         # plt.axis('equal')
#         sns.lineplot(x=data_range, y=y)
#         # for v1, v2 in zip(vertex1, vertex2):
#         #     sns.lineplot(x=np.array([v1[0], v2[0]]), y=np.array([v1[1], v2[1]]), color='k')
#         i += 1
#
# plt.tight_layout()
#
# plt.show()

plotter.link_views()
plotter.show()

# for center, random_length in zip(centers, random_lengths):
#
#     vertex1 = center.copy()
#     vertex1[0] -= random_length
#
#     vertex2 = center.copy()
#     vertex2[0] += random_length
#
#     line = pv.lines_from_points([vertex1, vertex2])
#     line['length'] = random_length
#     line_appender.AddInputData(line)
#
# line_appender.Update()
#
# outer_bounds_pv = pv.lines_from_points(outer_bounds)
# centers_pv = pv.PolyData(centers)
#
# plotter = pv.Plotter()
# plotter.add_mesh(outer_bounds_pv)
# plotter.add_mesh(line_appender.GetOutput())
# plotter.view_xy()
#
# plotter.add_camera_orientation_widget()
# plotter.show()