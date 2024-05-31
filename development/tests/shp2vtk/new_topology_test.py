import pandas as pd
import pyvista as pv
import geopandas as gpd
from pandas import concat
import numpy as np
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkCleanPolyData, vtkAppendPolyData, vtkIdFilter
import time
import itertools
from vtk.util import numpy_support


def shp2vtk(df: gpd.GeoDataFrame, nodes=False) -> pv.PolyData:
    """
    Quickly convert a GeoDataFrame to a PolyData
    :param df: input GeoDataFrame
    :param nodes: the input GeoDataFrame have Point type geometries set this to True
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

    keys = first_repeats['points'].values
    values = first_repeats['indexes'].values

    unique_values_dict = dict(zip(keys, values))

    # to change the indexes as the ones that are in the dict we get the values from the dict with apply(get)
    # and fill the na with the index column (i.e. the indexes that are not in common).
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


# fractures = gpd.read_file('Data/Salza/output/shp/Fractures.shp')
fractures = gpd.read_file('Data/Pontrelli/output/shp/Fractures_1.shp')
# center = fractures.dissolve().centroid
# fractures = fractures.translate(*-center.geometry.get_coordinates().values[0])
# boundary = gpd.read_file('Data/Salza/output/shp/Boundary.shp')
boundary = gpd.read_file('Data/Pontrelli/output/shp/Boundary_1.shp')
# boundary = boundary.translate(*-center.geometry.get_coordinates().values[0])
#
#
#
# fractures = gpd.read_file('Data/fractures.shp')
# boundary = gpd.read_file('Data/bounds.shp')

fractures_vtk = shp2vtk(fractures)
boundary_vtk = shp2vtk(boundary)


ids = []
c = 0
start = time.time()

for i, cell in enumerate(fractures_vtk.cell):
    cell_ids = cell.point_ids
    ids.append([cell_ids[0]])
    ids.append([cell_ids[-1]])
    ids.append(cell_ids)

ids = list(itertools.chain.from_iterable(ids))

u, c = np.unique(ids, return_counts=True)

ids = u[c > 1]



fracture_points = fractures_vtk.points
boundary_points = boundary_vtk.points


boundary_common = np.isin(np.round(fracture_points, 5), np.round(boundary_points, 5)).all(axis=1)
boundary_index = np.where(boundary_common == 1)[0]

print(boundary_index)

# print(fracture_points[boundary_index])

fractures_segm = fractures_vtk.extract_all_edges(use_all_points=True)
fractures_vtk['origin'] = np.zeros(fractures_vtk.n_points, dtype=int)
fractures_vtk['topology'] = np.zeros(fractures_vtk.n_points)


for i in range(fractures_vtk.n_points):
    neigh = fracture_points[fractures_segm.point_neighbors(i)]
    if len(neigh) != 2:
        fractures_vtk['topology'][i] = len(neigh)

end = time.time()

print(end-start)

fractures_vtk['topology'][boundary_index] = 5

censored_lines = [fractures_vtk.point_cell_ids(idx) for idx in boundary_index]
print(censored_lines)
fractures_vtk['censored'][censored_lines] = 1


fn = pv.MultiBlock({'fractures': fractures_vtk,
                    'boundary': boundary_vtk})

class_dict = {
    0: 'nan',
    1: 'I',
    2: 'V',
    3: 'Y',
    4: 'X',
    5: 'U',
    6: 'Y2'
}

cmap_dict = {
    'nan': 'None',
    'I': 'Blue',
    'Y': 'Green',
    'Y2': 'Cyan',
    'X': 'Red',
    'U': 'Yellow'
}


class_names = [class_dict[int(i)] for i in fractures_vtk['topology']]

used_tags = list(set(class_names))
used_tags.sort()
cmap = [cmap_dict[i] for i in used_tags]

sargs = dict(interactive=False,
             vertical=False,
             height=0.1,
             title_font_size=16,
             label_font_size=14)

plotter = pv.Plotter()
plotter.add_mesh(fn['fractures'], scalars='censored', line_width=2)
plotter.add_mesh(fn['boundary'], color='r', line_width=2)
plotter.add_points(fracture_points[boundary_index])
plotter.add_mesh(fn['fractures'], scalars=class_names,
                 render_points_as_spheres=False,
                 point_size=7,
                 show_scalar_bar=True,
                 scalar_bar_args=sargs,
                 cmap=cmap, style='points')
# plotter.add_mesh(test, color='y', line_width=3)

# plotter.add_mesh(points, color='blue', point_size=10)
plotter.add_camera_orientation_widget()
plotter.enable_image_style()
plotter.view_xy()
plotter.show()

# fractures_vtk.save('fractures.vtk')

# fractures_vtk.cell_data['f_set'] = fractures['f_set']
# fractures_vtk.cell_data['type'] = fractures['type']
#

# boundary_vtk.cell_data['b_group'] = boundary['b_group']
# boundary_vtk.cell_data['type'] = boundary['type']

