import geopandas as gpd
from vtk2shp import shp2vtk



fractures = gpd.read_file('Data/Salza/output/shp/Fractures.shp')
boundary = gpd.read_file('Data/Salza/output/shp/Boundary.shp')

get_coord_df_fracs = fractures.geometry.get_coordinates(ignore_index=False, index_parts=True)

fractures_vtk = shp2vtk(fractures)
boundary_vtk = shp2vtk(boundary)

print(f'{get_coord_df_fracs["x"][0][0]:.100f}')
print(f'{fractures_vtk.points[0][0]:.100f}')