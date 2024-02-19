import numpy as np
import shapely.geometry as geom
from shapely.affinity import scale
from shapely.ops import split
import geopandas as gpd
import matplotlib.pyplot as plt

def int_node(line1, line2, idx_list):
    """
    Function used to add the intersection node to a line crossed or touched by a second line.
    This function works by extending of a given factor the start and end segment the line2 and then use shapely to:

    1. Split line1 with line2
    2. Join the two split geometries

    We do this to identify and add the intersection node to line1:

    O----------O --split--> O-----O O-----O --join--> O-----O-----O

    The extension is used in case the joint is a Y or T and the positioning of the node is not pixel perfect. Depending
    on the number of segment composing line2 we extend in different ways:

    1. Only one segment extend the whole thing using the start and end vertex
    2. Two segments extend the two segments using the end of the first and the start of the second.
    3. Three or more segments extend the first and last segment using the end of the first and the start of the last.
    """
    new_geom_dict = {}
    fac = 1.05
    if line1.crosses(line2):
        split_lines1 = split(line1, line2)
        outcoords1 = [list(i.coords) for i in split_lines1.geoms]
        split_lines2 = split(line2, line1)
        outcoords2 = [list(i.coords) for i in split_lines2.geoms]

        new_line1 = geom.LineString([i for sublist in outcoords1 for i in sublist])
        new_line2 = geom.LineString([i for sublist in outcoords2 for i in sublist])
        new_geom_dict[idx_list[0]] = new_line1
        new_geom_dict[idx_list[1]] = new_line2
    else:
        for counter in range(3):
            if len(line2.coords) == 2:
                scaled_segment1 = scale(line2, xfact=fac, yfact=fac, origin=line2.boundary.geoms[0])
                scaled_segment2 = scale(scaled_segment1, xfact=fac, yfact=fac, origin=scaled_segment1.boundary.geoms[1])
                extended_line = geom.LineString(scaled_segment2)
            elif len(line2.coords) == 3:
                first_seg = geom.LineString(line2.coords[:2])
                last_seg = geom.LineString(line2.coords[-2:])
                scaled_first_segment = scale(first_seg, xfact=fac, yfact=fac, origin=first_seg.boundary.geoms[1])
                scaled_last_segment = scale(last_seg, xfact=fac, yfact=fac, origin=last_seg.boundary.geoms[0])
                extended_line = geom.LineString([*scaled_first_segment.coords, *scaled_last_segment.coords])
            else:
                first_seg = geom.LineString(line2.coords[:2])
                last_seg = geom.LineString(line2.coords[-2:])
                # print(np.array(first_seg.boundary.geoms), idx_list)
                scaled_first_segment = scale(first_seg, xfact=fac, yfact=fac, origin=first_seg.boundary.geoms[1])
                scaled_last_segment = scale(last_seg, xfact=fac, yfact=fac, origin=last_seg.boundary.geoms[0])
                extended_line = geom.LineString(
                    [*scaled_first_segment.coords, *line2.coords[2:-2], *scaled_last_segment.coords])

            split_lines = split(line1, extended_line)

            # Check if the selected line combination defined an intersection. If not, switch the lines.
            # If again no intersection is found then there is no intersection
            # If found then create a LineString composed of the two segments (we don't use merge because this is the
            # only way to be sure that no multipart object is created; merge creates multipart if the two points are not
            # exactly overlapping).

            if len(split_lines.geoms) == 1 and counter < 2:
                line1, line2 = line2, line1
            elif len(split_lines.geoms) == 1 and counter >= 2:
                print('ciao')
                new_geom_dict = {}
            else:
                outcoords = [list(i.coords) for i in split_lines.geoms]
                new_line = geom.LineString([i for sublist in outcoords for i in sublist])
                new_geom_dict[idx_list[counter]] = new_line

                # Plot results to visualize intersections

                test2 = np.array(extended_line.coords)
                test1 = np.array(new_line.coords)

                plt.plot(test1[:, 0], test1[:, 1], 'r-o')
                plt.plot(test2[:, 0], test2[:, 1], 'b-o')
                plt.show()

                break

        # print(gdf.loc[idx_list[0]-5:idx_list[1]+5])
    return new_geom_dict


f_1 = gpd.read_file('data/fn_1.shp').geometry[156]
f_2 = gpd.read_file('data/fn_2.shp').geometry[201]

test = int_node(f_1, f_2, [0, 1])
print(test)
# split_lines = split(f_1, f_2)
# outcoords = [list(i.coords) for i in split_lines.geoms]
# new_line = geom.LineString([i for sublist in outcoords for i in sublist])
# print(new_line)