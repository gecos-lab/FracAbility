from fracability.AbstractClasses import BaseEntity
from fracability.utils.shp_operations import int_node

from copy import deepcopy


# @Halo(text='Calculating intersections', spinner='line', placement='right')
def tidy_intersections(obj, buffer=0.05, inplace: bool = True):

    if obj.name == 'FractureNetwork':
        gdf = obj.fracture_network_to_components_df()
        gdf = gdf.loc[gdf['type'] != 'node']
    else:
        gdf = obj.entity_df.copy()

    df_buffer = gdf.buffer(buffer)

    for idx_line1, line in gdf.iterrows():

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

    if inplace:
        obj.entity_df = gdf
    else:
        copy_obj = deepcopy(obj)
        copy_obj.entity_df = gdf
        return copy_obj


def calculate_seg_length(obj: BaseEntity, inplace: bool = True):

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

