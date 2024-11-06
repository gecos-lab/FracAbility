import pyvista as pv
import geopandas as gpd

import numpy as np

import time
import itertools



def shp2vtk(df: gpd.GeoDataFrame, input_type:str=None) -> pv.PolyData:

    if input_type is None: # if no type is specified then it will be assumed from the first entry
        input_type = df.geom_type[0]

    # check if there are any inner rings for polygons
    if input_type == 'Polygon':
        check = df.interiors.apply(lambda x: len(x) == 0)

        if not check.all():
            print('Polygon with hole detected, converting Polygon shapefile to LineStrings')
            df['geometry'] = df.boundary
            df = df.explode()

        input_type = df.geom_type[0]

    n_geom_points = df.count_coordinates() # get the number of points for each geometry in the df

    idx = np.roll(n_geom_points.cumsum().values, 1) # get the cumulative sum of the n of points (necessary to know the n of segments in the connectivity list)
    idx[0] = 0

    xyz = np.zeros((n_geom_points.sum(), 3))
    conn = np.arange(0, n_geom_points.sum()) # get the connectivity list as range from 0 to n_points
    conn = np.insert(conn, idx, n_geom_points) # insert the number of points for each geometry at the desired (idx) position

    i = 0

    for geom in df.geometry:

        xy = get_coordinates(geom).reshape(-1, 2)
        z = np.zeros((len(xy), 1))

        points = np.hstack((xy, z))
        n_points = len(points)

        xyz[i:i + n_points] = points

        i += n_points

    match input_type:
        case 'Point':
            pv_obj = pv.PolyData(xyz, verts=conn)
        case 'LineString':
            pv_obj = pv.PolyData(xyz, lines=conn)
        case 'Polygon':
            pv_obj = pv.PolyData(xyz, faces=conn)

    gpd_indexes = df.index.values
    properties_cols = df.drop('geometry', axis=1).columns

    pv_obj.cell_data['index'] = gpd_indexes
    pv_obj.field_data['type'] = input_type

    for col in properties_cols:
        pv_obj.cell_data[col] = df[col].values

    return pv_obj


fractures = gpd.read_file('../../Shapefiles/Salza_in/Set_1.shp')
# fractures = gpd.read_file('../../Shapefiles/Pontrelli_in/Set_a.shp')
# center = fractures.dissolve().centroid
# fractures = fractures.translate(*-center.geometry.get_coordinates().values[0])
boundary = gpd.read_file('../../Shapefiles/Salza_in/Interpretation_boundary.shp')
# boundary = gpd.read_file('../../Shapefiles/Pontrelli_in/Interpretation_boundary.shp')
# boundary = boundary.translate(*-center.geometry.get_coordinates().values[0])


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

