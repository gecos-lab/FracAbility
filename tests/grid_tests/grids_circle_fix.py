import pyvista as pv
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, MultiLineString
import matplotlib.pyplot as plt
from vtkmodules.vtkFiltersCore import vtkAppendPolyData

min_rad = 0.1
max_rad = 0.5
n_points = 50


rads = np.linspace(min_rad, max_rad, 6)

data = gpd.read_file('grid_pesce_grosso.shp')
fracs = gpd.read_file('Laghetto_Salza_Fracture_mapping/Fracture_network.shp')


center = np.array(data.centroid[0].coords).flatten()


data = data.translate(-center[0], -center[1])


fracs = fracs.translate(-center[0], -center[1])

frac_appender = vtkAppendPolyData()
for frac in fracs.geometry:
    xy = np.array(frac.coords)
    xyz = np.hstack((xy, np.zeros((len(xy), 1))))
    frac = pv.lines_from_points(xyz)
    frac_appender.AddInputData(frac)
frac_appender.Update()

boundary = data[0]
boundary_contour = boundary.boundary

if isinstance(boundary_contour, MultiLineString):
    lines = [line for line in boundary_contour.geoms]
else:
    lines = [boundary_contour]
#
plotter = pv.Plotter()

for boundary_contour in lines:

    boundary_buffer = boundary_contour.buffer(max_rad)

    points = []
    centers = []
    minx, miny, maxx, maxy = boundary.bounds

    while len(points) < n_points:
        center = np.random.uniform(minx, maxx), np.random.uniform(miny, maxy), 0
        pnt = Point(center)
        pnt_buff = pnt.buffer(max_rad)
        if boundary.contains(pnt_buff):
            points.append(pnt)
            centers.append(center)

    appender = vtkAppendPolyData()

    for r in rads:
        for center in centers:

            circle = pv.Disc(center=center, inner=r*0.95, outer=r, c_res=100)
            circle.cell_data['rad'] = [r] * circle.GetNumberOfCells()
            appender.AddInputData(circle)
        appender.Update()

        plotter.add_mesh(appender.GetOutput())

    xy = np.array(boundary_contour.coords)
    xyz = np.hstack((xy, np.zeros((len(xy), 1))))

    # print(xyz)
    boundary_poly = pv.lines_from_points(xyz)

    plotter.add_mesh(boundary_poly)

plotter.add_mesh(frac_appender.GetOutput())
plotter.set_background('gray')
plotter.view_xy()
plotter.add_camera_orientation_widget()
plotter.show()