from copy import deepcopy

from pyvista import PolyData
from vtkmodules.vtkFiltersCore import vtkCleanPolyData

from fracability.AbstractClasses import BaseEntity
from fracability.utils.shp_operations import int_node

def connect_dots(vtk_obj: PolyData) -> PolyData:

    """Method used to clean intersection in vtk objects (for example merge two overlapping nodes)"""

    p = 100000  # Scaling factor needed for the vtk function to work properly
    vtk_obj.points *= p
    clean = vtkCleanPolyData()
    clean.AddInputData(vtk_obj)
    clean.ToleranceIsAbsoluteOn()
    clean.ConvertLinesToPointsOff()
    clean.ConvertPolysToLinesOff()
    clean.ConvertStripsToPolysOff()
    clean.Update()

    output_obj = PolyData(clean.GetOutput())
    output_obj.points /= p  # Rescale back the points

    return output_obj


#@Halo(text='Calculating intersections', spinner='line', placement='right')
def tidy_intersections(obj, buffer=0.05, inplace: bool = True):
    """Method used to tidy shapefile intersections between fractures in a fracture or fracture network object."""

    if obj.name == 'FractureNetwork':
        gdf = obj.fracture_network_to_components_df()
        gdf = gdf.loc[gdf['type'] != 'node']
    elif obj.name == 'Fractures':
        gdf = obj.entity_df.copy()
    else:
        print('Cannot tidy intersection for nodes or only boundaries')
        return

    df_buffer = gdf.buffer(buffer)
    print('\n\n')
    for idx_line1, line in gdf.iterrows():
        print(f'Calculating intersections on fracture: {idx_line1+1}/{len(gdf.index)}', end='\r')

        if line['type'] == 'boundary':
            continue

        line1 = line['geometry']

        idx_list = df_buffer.index[df_buffer.intersects(line1) == True]  # Subset the intersecting lines
        idx_list = idx_list[idx_list != idx_line1]  # Exclude the reference line index to avoid self intersection

        intersections = gdf.loc[idx_list]
        for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:
            new_geom = int_node(line1, line2, [idx_line1, idx_line2], gdf)  # Calculate and add the intersection node.

            for key, value in new_geom.items():
                gdf.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry

            line1 = gdf.loc[
                idx_line1, 'geometry']  # Use as the reference line (in the int_node function) the new geometry.

    print('\n\n')

    if inplace:
        obj.entity_df = gdf
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = gdf
        return copy_obj

def tidy_intersections_boundary_only(obj, buffer=0.05, inplace: bool = True):
    """Method used to tidy shapefile intersections with the boundary of a fracture or fracture network object."""
    if obj.name == 'FractureNetwork':
        gdf = obj.fracture_network_to_components_df()
        gdf = gdf.loc[gdf['type'] != 'node']
    elif obj.name == 'Fractures':
        gdf = obj.entity_df.copy()
    else:
        print('Cannot tidy intersection for nodes or only boundaries')
        return
    df_buffer = gdf.buffer(buffer)
    print('\n\n')
    for idx_line1, line in gdf.iterrows():
        print(f'Calculating intersections on fracture: {idx_line1+1}/{len(gdf.index)}', end='\r')

        if line['type'] == 'boundary':
            continue

        line1 = line['geometry']

        idx_list = df_buffer.index[df_buffer.intersects(line1) == True]  # Subset the intersecting lines
        idx_list = idx_list[idx_list != idx_line1]  # Exclude the reference line index to avoid self intersection

        intersections = gdf.loc[idx_list]
        for line2, idx_line2 in zip(intersections['geometry'], idx_list):  # for each intersecting line:
            if intersections['type'][idx_line2] == 'boundary':
                new_geom = int_node(line1, line2, [idx_line1, idx_line2], gdf)  # Calculate and add the intersection node.

                for key, value in new_geom.items():
                    gdf.loc[key, 'geometry'] = value  # substitute the original geometry with the new geometry

                line1 = gdf.loc[
                    idx_line1, 'geometry']  # Use as the reference line (in the int_node function) the new geometry.
            else:
                continue
    print('\n\n')
    if inplace:
        obj.entity_df = gdf
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = gdf
        return copy_obj


def calculate_seg_length(obj: BaseEntity, inplace: bool = True):
    """Method used to calculate and set fracture lengths when absent"""

    if obj.name == 'FractureNetwork':
        gdf = obj.fracture_network_to_components_df()
        gdf = gdf.loc[gdf['type'] != 'node']
        gdf = gdf.loc[gdf['type'] != 'boundary']
    elif obj.name == 'Nodes':
        print('cannot calculate lengths of nodes')
        return
    else:
        gdf = obj.entity_df.copy()

    df = gdf.copy()

    if 'lengths' in df.columns:
        print('length column already present. Delete it to recalculate lengths')
    else:
        df['lengths'] = df.length

    if inplace:
        obj.entity_df = df
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = df
        return copy_obj

