import geopandas as gpd
import pyvista as pv
import numpy as np
from shapely import get_coordinates, LineString, Point, Polygon
import matplotlib.pyplot as plt

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

def vtk2shp(vtk_repr: pv.PolyData, input_type:str=None) -> gpd.GeoDataFrame:
    cell_dict = dict(vtk_repr.cell_data)

    if input_type is None:
        input_type = vtk_repr.field_data['type']

    gdf = gpd.GeoDataFrame(cell_dict)

    for cell_id in range(vtk_repr.n_cells):
        cell = vtk_repr.extract_cells(cell_id)

        points = cell.points
        conn = cell.cell_connectivity
        match input_type:
            case 'Point':
                geom = Point(points[conn])
            case 'LineString':
                geom = LineString(points[conn])
            case 'Polygon':
                geom = Polygon(points[conn])

        gdf.loc[cell_id, 'geometry'] = geom

    gdf.set_index('index', inplace=True)
    gdf.set_geometry('geometry')

    return gdf



if __name__=='__main__':
    # shp_points = gpd.read_file('shp/points.shp')

    shp_lines = gpd.read_file('../../Shapefiles/Pontrelli_in/Set_a.shp')

    print(shp_lines)

    # shp_polys = gpd.read_file('shp/poly.shp')


    vtk_obj = shp2vtk(shp_lines)

    vtk_obj.plot(scalars='censored')

    shp_repr = vtk2shp(vtk_obj)
    print(shp_repr)


