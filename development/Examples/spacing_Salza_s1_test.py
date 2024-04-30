"""
Python code to calculate the spacing distribution of a given linear fracture set.
"""
import os
import sys

cwd = os.path.dirname(os.getcwd())
sys.path.append(cwd)


from fracability import DATADIR
from fracability import Entities
from fracability.operations import Statistics
from fracability.Plotters import matplot_stats_uniform, matplot_stats_table
import geopandas as gpd
import numpy as np
from shapely.ops import split
import pyvista as pv


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


data_path = f'{DATADIR}/laghetto_salza/Set_1.shp'
boundary_path = f'{DATADIR}/laghetto_salza/Interpretation_boundary.shp'

df = gpd.read_file(data_path)
boundary_df = gpd.read_file(boundary_path)

length_plane = 70  # E-W extension of the outcrop
length_scanl = 70  # N-S extension of the outcrop
resolution = 50  # Number of scanlines along the direction


mean_dir = np.mean(np.floor(df['azimuth']))
# mean_dir = 45
scanline_dir = (mean_dir+90) % 360

fractures = Entities.Fractures(gdf=df, set_n=1)

directions = fractures.entity_df['azimuth'] % 180

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
boundary_shps = boundary_df['geometry'].translate(-frac_center[0], -frac_center[1])


fractures_diss = fractures.entity_df.dissolve()

split_scanlines_list = []


for scanline in scanlines_shp:
    split_geom = split(scanline, fractures_diss['geometry'].values[0])
    for segment in split_geom.geoms:
        for boundary_shp in boundary_shps:
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
# plotter.background_color = 'Gray'
# plotter.show()

frac_net = Entities.FractureNetwork()
frac_net.add_fractures(valid_scanlines)
frac_net.add_boundaries(boundary)

frac_net.calculate_topology()
frac_net.vtk_plot()

frac_net.fractures.save_csv('Spacing_Salza_S1')

fitter = Statistics.NetworkFitter(frac_net)
fitter.fit('lognorm')
fitter.fit('expon')
fitter.fit('weibull_min')
fitter.fit('gamma')
fitter.fit('norm')
fitter.fit('powerlaw')

matplot_stats_table(fitter)
# matplot_stats_uniform(fitter)
#
# print(fitter.fit_records)