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


def plot_rose(dir_data):
    bin_edges = np.arange(-5, 366, 10)
    number_of_strikes, bin_edges = np.histogram(dir_data, bin_edges)
    number_of_strikes[0] += number_of_strikes[-1]
    half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
    two_halves = np.concatenate([half, half])
    fig = plt.figure(figsize=(16, 8))

    ax = fig.add_subplot(111, projection='polar')

    ax.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves,
           width=np.deg2rad(10), bottom=0.0, color='.8', edgecolor='k')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title('Rose Diagram of the "Fault System"', y=1.10, fontsize=15)

    fig.tight_layout()
    plt.show()


def histogram(dir_data):
    sns.histplot(dir_data, bins=18)
    plt.show()


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


data_path = 'data/cava_pontrelli/FN_set_1.shp'
boundary_path = 'data/cava_pontrelli/Interpretation-boundary.shp'

df = gpd.read_file(data_path)
boundary_df = gpd.read_file(boundary_path)

length_plane = 120
length_scanl = 150
resolution = 10


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
for scanline in scanlines_shp:
    split_geom = split(scanline, boundary_shp)
    for segment in split_geom.geoms:
        if boundary_shp.covers(segment):
            split_segment = split(segment, fractures_diss['geometry'].values[0])
            split_scanlines_list.append(list(split_segment.geoms))

split_scanlines_df = gpd.GeoDataFrame(geometry=np.concatenate(split_scanlines_list))

valid_scanlines = Entities.Fractures(gdf=split_scanlines_df,set_n=1)

frac_net = Entities.FractureNetwork()
# frac_net.add_fractures(valid_scanlines)
frac_net.add_fractures(scanlines)
frac_net.add_boundaries(boundary)

frac_net.fractures.vtk_plot()

# frac_net.calculate_topology()
#
#
# fitter = Statistics.NetworkFitter(frac_net)
# fitter.fit('lognorm')
# matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))

#
#
# fractures_diss = fractures.entity_df.dissolve()
# splitted_list = []
#
# for i, scanline in enumerate(scanlines.entity_df['geometry'].values):
#
#     splitted = split(scanline, fractures_diss['geometry'].values[0])
#     splitted_list.append(list(splitted.geoms))
#
# scanline_df = gpd.GeoDataFrame(geometry=np.concatenate(splitted_list))
#
# new_scanlines = Entities.Fractures(gdf=scanline_df, set_n=4)
#
#
#
# frac_net = Entities.FractureNetwork()
# frac_net.add_fractures(new_scanlines)
# frac_net.add_boundaries(boundary)
# print(frac_net.sets)
# frac_net.cut_net_on_boundary()
# frac_net.vtk_plot()

# frac_net.calculate_topology()
# sns.histplot(new_scanlines.entity_df['length'].values)
# plt.show()


# fitter = Statistics.NetworkFitter(frac_net)
# fitter.fit('lognorm')
# matplot_stats_summary(fitter.get_fitted_distribution('lognorm'))

# print(new_scanlines.vtk_object.array_names)
#
# plotter = pv.Plotter()
# plotter.background_color = 'gray'
# plotter.add_mesh(boundary.vtk_object, color='white')
# # plotter.add_mesh(line, color='r')
# # # plotter.add_mesh(mean_plane, color='b')
# # # plotter.add_points(test_points, color='y')
# plotter.add_mesh(lines)
# plotter.view_xy()
# plotter.enable_image_style()
# plotter.show()
