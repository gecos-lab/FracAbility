"""
Python code to calculate the spacing distribution of a given linear fracture set.
"""
import pandas as pd
from fracability import Entities
from fracability.operations import Statistics
from fracability.Plotters import matplot_stats_summary
import geopandas as gpd
import numpy as np
from shapely.ops import split
import pyvista as pv
import matplotlib.pyplot as plt
import seaborn as sns

from vtkmodules.vtkFiltersModeling import vtkCookieCutter


def centers_to_lines(center_coords, lengths, frac_dir, assign_id=True) -> pv.PolyData:
    """ Function used to create fractures of given lengths from center coordinates.

    :param center_coords: xyz coordinate centers array of the fractures
    :param lengths: length array for each fracture.
    :param frac_dir: direction array of each fracture.
    :param assign_id: Flag used to assign the id of each fracture as a field (RegionId). Default True

    :return: Pyvista polydata with the same number of fracture as centers.
    """

    half_lengths = lengths/2
    xyz1 = center_coords.copy()
    xyz2 = center_coords.copy()

    xyz1[:, 0] = center_coords[:, 0] + half_lengths * np.sin(np.deg2rad(frac_dir))
    xyz2[:, 0] = center_coords[:, 0] + half_lengths * np.sin(np.deg2rad((frac_dir + 180) % 360))

    xyz1[:, 1] = center_coords[:, 1] + half_lengths * np.cos(np.deg2rad(frac_dir))
    xyz2[:, 1] = center_coords[:, 1] + half_lengths * np.cos(np.deg2rad((frac_dir + 180) % 360))

    xyz_complete = np.array([[i, j] for i, j in zip(xyz1, xyz2)]).reshape(-1, 3)
    conn = np.insert(np.arange(0, len(xyz_complete)), np.arange(0, len(xyz_complete), 2), 2)
    lines = pv.PolyData(xyz_complete, lines=conn)

    if assign_id:
        regions_ids = np.arange(0, len(center_coords))
        lines['RegionId'] = regions_ids

    return lines


def center_points(center_coords, lengths, dir, resolution=10):
    """Function used to create a series of points along a line with center, length and direction."""

    center_coords = center_coords.flatten()
    beta = np.deg2rad(dir-90)
    l = lengths/2
    x1 = center_coords[0]-l*np.cos(beta)
    y1 = center_coords[1]+l*np.sin(beta)

    x2 = center_coords[0]+l*np.cos(beta)
    y2 = center_coords[1]-l*np.sin(beta)

    x_range = np.linspace(x1, x2, resolution)
    y_range = np.linspace(y1, y2, resolution)
    z_range = np.zeros_like(x_range)

    xyz = np.column_stack((x_range, y_range, z_range))

    return xyz


data_path = '../../src/datasets/cava_pontrelli/Set_a.shp'
boundary_path = '../../src/datasets/cava_pontrelli/Interpretation-boundary.shp'

df = gpd.read_file(data_path)
boundary_df = gpd.read_file(boundary_path)

length_plane = 150
length_scanl = 170
resolution = 100


df_faults = df.loc[df['Fault'] == 1]
# df_joints = df.loc[df['Fault'] == 0]

mean_dir = np.mean(np.floor(df['dir']))
# mean_dir = 45
scanline_dir = (mean_dir+90) % 360

# fractures = Entities.Fractures(gdf=df, set_n=1)
fractures = Entities.Fractures(gdf=df_faults, set_n=1)
# fractures = Entities.Fractures(gdf=df_joints, set_n=1)

directions = fractures.entity_df['dir'] % 180

frac_center = fractures.center_object(return_center=True)

set_center = np.insert(fractures.centroid, 0, 0).reshape(-1, 3)
mean_plane = centers_to_lines(set_center, length_plane, frac_dir=mean_dir)
test_points = center_points(set_center, length_plane, mean_dir, resolution)
lines = centers_to_lines(test_points, length_scanl, frac_dir=scanline_dir)

boundary = Entities.Boundary(shp=boundary_path)
boundary.center_object(trans_center=frac_center)

scanlines = Entities.Fractures()
scanlines.vtk_object = lines

scanlines_shp = scanlines.entity_df['geometry'].values
boundary_shp = boundary_df['geometry'].translate(-frac_center[0], -frac_center[1]).values[0]


fractures_diss = fractures.entity_df.dissolve()

split_scanlines_list = []

# for scanline in scanlines_shp:
#     split_geom = split(scanline, boundary_shp)
#     for segment in split_geom.geoms:
#         if boundary_shp.buffer(0.001).contains(segment):
#             split_scanlines_list.append(segment)

for scanline in scanlines_shp:
    split_geom = split(scanline, fractures_diss['geometry'].values[0])
    for segment in split_geom.geoms:
        split_segment = split(segment, boundary_shp)
        for line in split_segment.geoms:
            if boundary_shp.buffer(0.001).contains(line):
                split_scanlines_list.append(line)


split_scanlines_df = gpd.GeoDataFrame(geometry=split_scanlines_list)

valid_scanlines = Entities.Fractures(gdf=split_scanlines_df, set_n=1)

# plotter = pv.Plotter()
# plotter.add_mesh(fractures.vtk_object, color='white')
# plotter.add_mesh(boundary.vtk_object, color='red')
# plotter.add_mesh(valid_scanlines.vtk_object, color='yellow')
# plotter.add_camera_orientation_widget()
# plotter.show()

frac_net = Entities.FractureNetwork()
frac_net.add_fractures(valid_scanlines)
frac_net.add_fractures(scanlines)
frac_net.add_boundaries(boundary)

# print(len(frac_net.fractures.entity_df['length']))
# frac_net.vtk_plot()
frac_net.calculate_topology()

# print(frac_net.fraction_censored)
#
fitter = Statistics.NetworkFitter(frac_net)
fitter.fit('lognorm')
matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))
