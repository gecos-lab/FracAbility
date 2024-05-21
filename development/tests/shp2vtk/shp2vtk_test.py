import pyvista as pv
import geopandas as gpd
import pandas as pd
import numpy as np
from vtkmodules.vtkFiltersCore import vtkCleanPolyData

from fracability import Entities


def shp2vtk(df: gpd.GeoDataFrame, nodes=False) -> pv.PolyData:
    """
    Quickly convert a GeoDataFrame to a PolyData
    :param df: input GeoDataFrame
    :return: PolyData.
    """
    get_coord_df = df.geometry.get_coordinates(ignore_index=False, index_parts=True)
    get_coord_df.reset_index(inplace=True)
    get_coord_df.columns = ['parts', 'indexes', 'x', 'y']
    get_coord_df['indexes'] = range(0, len(get_coord_df))
    get_coord_df['parts'] += 1

    get_coord_df['z'] = np.zeros(len(get_coord_df['x']))
    get_coord_df['points'] = get_coord_df.loc[:, ['x', 'y', 'z']].values.tolist()
    get_coord_df['points'] = get_coord_df['points'].map(tuple)
    duplicate_mask_first = get_coord_df.duplicated(subset=['x', 'y', 'z'], keep='last')
    first_repeats = get_coord_df[duplicate_mask_first]
    # other_repeats = get_coord_df[duplicate_mask_other]

    values = first_repeats['indexes'].values
    keys = first_repeats['points'].values

    unique_values_dict = dict(zip(keys, values))

    # to change the indexes as the ones that are in the dict we get the values from the dict with apply(get) and fill the na with the index column.
    get_coord_df['indexes'] = get_coord_df['points'].apply(func=lambda x: unique_values_dict.get(x)).fillna(
        get_coord_df['indexes']).astype(int)

    mem = 0
    conn = list()
    for part, index in zip(get_coord_df['parts'], get_coord_df.index):
        if part != mem:
            nparts = len(get_coord_df[get_coord_df['parts'] == part])
            conn.append(nparts)
        conn.append(get_coord_df.loc[index, 'indexes'])
        mem = part

    points = np.array(get_coord_df.loc[:, ['x', 'y', 'z']].values.tolist())
    if nodes:
        vtk_obj = pv.PolyData(points)
    else:
        vtk_obj = pv.PolyData(points, lines=conn)

    arrays = list(df.columns)
    arrays.remove('geometry')
    for array in arrays:
        vtk_obj[array] = df[array].values

    p = 100000  # Scaling factor needed for the vtk function to work properly
    vtk_obj.points *= p
    clean = vtkCleanPolyData()
    clean.AddInputData(vtk_obj)
    clean.ToleranceIsAbsoluteOn()
    clean.ConvertLinesToPointsOff()
    clean.ConvertPolysToLinesOff()
    clean.ConvertStripsToPolysOff()
    clean.Update()

    output_obj = pv.PolyData(clean.GetOutput())
    output_obj.points /= p  # Rescale back the points
    return output_obj


fractures = gpd.read_file('Data/Salza/output/shp/Fractures.shp')
boundary = gpd.read_file('Data/Salza/output/shp/Boundary.shp')
nodes = gpd.read_file('Data/Salza/output/shp/Nodes.shp')

# print(list(fractures.columns).remove('geometry'))

fractures_vtk = shp2vtk(fractures)

boundary_vtk = shp2vtk(boundary)

nodes_vtk = shp2vtk(nodes, nodes=True)

fn = pv.MultiBlock({'fractures': fractures_vtk,
                    'boundary': boundary_vtk,
                    'nodes': nodes_vtk})

plotter = pv.Plotter()
plotter.add_mesh(fn['fractures'], color='k')
# plotter.add_mesh(fn['boundary'], color='r')
plotter.add_mesh(fn['nodes'], point_size=7)


# plotter.add_mesh(points, color='blue', point_size=10)
plotter.add_camera_orientation_widget()
plotter.enable_image_style()
plotter.view_xy()

plotter.show()




