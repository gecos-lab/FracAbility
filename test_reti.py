import geopandas as gpd
from pandas import concat as pd_concat
import shapely.geometry as geom
from shapely.affinity import scale
from shapely.ops import split
import time
from datetime import datetime
from vtkmodules.all import *
import pyvista as pv


# import ternary
import networkx as net

import numpy as np
import ternary


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
    try:
        if line1.crosses(line2):
            split_lines1 = split(line1, line2)
            outcoords1 = [list(i.coords) for i in split_lines1]
            split_lines2 = split(line2, line1)
            outcoords2 = [list(i.coords) for i in split_lines2]

            new_line1 = geom.LineString([i for sublist in outcoords1 for i in sublist])
            new_line2 = geom.LineString([i for sublist in outcoords2 for i in sublist])
            new_geom_dict[idx_list[0]] = new_line1
            new_geom_dict[idx_list[1]] = new_line2
        else:
            for counter in range(3):
                if len(line2.coords) == 2:
                    scaled_segment1 = scale(line2, xfact=fac, yfact=fac, origin=line2.boundary[0])
                    scaled_segment2 = scale(scaled_segment1, xfact=fac, yfact=fac, origin=scaled_segment1.boundary[1])
                    extended_line = geom.LineString(scaled_segment2)
                elif len(line2.coords) == 3:
                    first_seg = geom.LineString(line2.coords[:2])
                    last_seg = geom.LineString(line2.coords[-2:])
                    scaled_first_segment = scale(first_seg, xfact=fac, yfact=fac, origin=first_seg.boundary[1])
                    scaled_last_segment = scale(last_seg, xfact=fac, yfact=fac, origin=last_seg.boundary[0])
                    extended_line = geom.LineString([*scaled_first_segment.coords, *scaled_last_segment.coords])
                else:
                    first_seg = geom.LineString(line2.coords[:2])
                    last_seg = geom.LineString(line2.coords[-2:])

                    scaled_first_segment = scale(first_seg, xfact=fac, yfact=fac, origin=first_seg.boundary[1])
                    scaled_last_segment = scale(last_seg, xfact=fac, yfact=fac, origin=last_seg.boundary[0])
                    extended_line = geom.LineString([*scaled_first_segment.coords, *line2.coords[2:-2], *scaled_last_segment.coords])

                split_lines = split(line1, extended_line)

                # Check if the selected line combination defined a intersection. If not, switch the lines.
                # If again no intersection is found then there is no intersection
                # If found then create a LineString composed of the two segments (we don't use merge because this is the
                # only way to be sure that no multipart object is created; merge creates multipart if the two points are not
                # exactly overlapping).
                if len(split_lines) == 1 and counter <2:
                    line1, line2 = line2, line1
                elif len(split_lines) == 1 and counter >=2:
                    new_geom_dict = {}
                else:
                    outcoords = [list(i.coords) for i in split_lines]
                    new_line = geom.LineString([i for sublist in outcoords for i in sublist])
                    new_geom_dict[idx_list[counter]] = new_line

                    # # Plot results to visualize intersections

                    # test2 = np.array(extended_line.coords)
                    # test1 = np.array(new_line.coords)
                    #
                    # plt.plot(test1[:, 0], test1[:, 1], 'r-o')
                    # plt.plot(test2[:, 0], test2[:, 1], 'b-o')
                    # plt.show()


                    break

    except (ValueError, TypeError):
        print(f'Geometry error for {idx_list}, classification may be inaccurate.')
        new_geom_dict = {}
    except NotImplementedError:
        print(f'Multipart geometry found {idx_list}. Terminating')
        exit()
    except IndexError:
        print(f'Duplicate points fount {idx_list}. Terminating')
        exit()

    return new_geom_dict

# Input shp files

# data = 'test_extract.shp'
# data = 'test_extract2.shp'
# data = 'test_extract3.shp'

# data = 'attachments_arc/Test_topologia.shp'
# bound_data = 'attachments_arc/Test_topologia_bound.shp'

# data = 'attachments/Fracture_network_simp.shp'


# data = 'test_bounds_net.shp'
# bound_data = 'test_bounds.shp'
#
data = 'rerobe/Fracture_network.shp'
# data = 'attachments/Set_2.shp'

bound_data = 'rerobe/Interpretation_boundary_laghettoSalza.shp'
# data = 'Betta_01_Fracture_mapping/Fracture_network_tot_no_dup.shp'
# bound_data = 'Betta_01_Fracture_mapping/Interpretation_boundary_tot.shp'
# bound_data = ''


# data = 'nord/Fracture_Network_convert_no_vert.shp'
# data = 'Malta_Victoria_N/merge_lstr_no_verts.shp'


# Create pyvista plotter to plot the results
# plotter = pv.Plotter(shape=(1,2))
plotter = pv.Plotter()
start = time.time()
print('1. Importing data')

# Read shp file with geopandas -> Similar to gis attribute table + associated geometry (line, polygon, etc..)
net_df = gpd.read_file(data)

if 'type' not in net_df.columns:
    net_df['type'] = 'network'

if 'U-nodes' not in net_df.columns:
    net_df['U-nodes'] = 0

if bound_data != '':
    bound_df = gpd.read_file(bound_data)

    boundaries = bound_df.boundary # boundaries must be provided as polygons
    bound_df['geometry'] = boundaries
    n = bound_df.shape[0]
    for i, geometry in enumerate(boundaries):
        if isinstance(geometry, geom.MultiLineString):
            bound_df.drop(index=i, inplace=True)
            # print(bound_df)
            for line in geometry:
                bound_df.loc[n, 'geometry'] = line
                n += 1
            # print(bound_df)
    if 'type' not in bound_df.columns:
        bound_df['type'] = 'boundary'
    df = gpd.GeoDataFrame(pd_concat([net_df[['geometry', 'type']], bound_df[['geometry', 'type']]], ignore_index=True))
    df['U-nodes'] = 0
else:
    df = net_df

if 'length' not in df.columns:
    df['length'] = df.length
else:
    print(max(df.length))
# test = df.iloc[1578]['geometry']
# idx_list = df.buffer(0.05).index[df.buffer(0.05).intersects(test) == True]  # Subset the intersecting lines
# intersections = df.iloc[idx_list]

# df = intersections



# center = df.dissolve().centroid

# df['geometry'] = df.translate(-np.array(center[0])[0], -np.array(center[0])[1])

df_buffer = df.buffer(0.05) # Create a buffer used to check which lines intersect.

total_seg = len(df)


print('2. Calculating intersections')

'''

We need to calculate and add the intersection nodes for each line of the dataset. This is done with a nested for loop:

1. For each line in the dataset a subset of intersecting line is selected
(idx_list = df_buffer.index[df_buffer.intersects(line) == True])
2. For each intersecting line the int_node function is applied and a new line geometry is created with the new found node
'''

df_buffer = df.buffer(0.05)  # Create a buffer used to check which lines intersect.
for idx_line1, line in df.iterrows():
    line1 = line['geometry']
    print(f'Processing {idx_line1+1}/{total_seg+1} segments', end='\r')
    # df_buffer.drop(index=idx_line1, inplace=True) # Remove the geometry to avoid self intersection

    idx_list = df_buffer.index[df_buffer.intersects(line1) == True] # Subset the intersecting lines
    idx_list = idx_list[idx_list != idx_line1]
    intersections = df.loc[idx_list]

    for line2, idx_line2 in zip(intersections['geometry'], idx_list): # for each intersecting line:

        new_geom = int_node(line1, line2, [idx_line1, idx_line2])  # Calculate and add the intersection node.

        for key, value in new_geom.items():
            df.loc[key, 'geometry'] = value # substitute the original geometry with the new geometry

        line1 = df.loc[idx_line1, 'geometry'] # Use as the reference line (in the int_node function) the new geometry.

# Plot results to visualize the network

# df.plot()

# for line in df['geometry']:
#     points = np.array(line.coords)
#     plt.plot(points[:, 0],points[:, 1],'-o')
#
# plt.show()

'''

Once all of the nodes are defined we create a vtk PolyData containing all of the different fracture segments.
We then:
 1. Calculate the connectivity to define each segment with a different region
 2. Clean the PolyData to fuse coincident points into one

'''

appender = vtkAppendPolyData()
p = 100000 # Scaling factor needed for the vtk functions to work properly

for line, l_type in zip(df['geometry'], df['type']): # For each geometry in the df

    x, y = line.coords.xy # get xy as an array
    z = np.zeros_like(x) # create a zeros z array with the same dim of the x (or y)

    points = np.stack((x, y, z), axis=1) # Stack the coordinates to a [n,3] shaped array
    points *= p # Multiply the coordinates with the factor
    # offset = np.round(points[0][0])
    pvline = pv.lines_from_points(points) # Create the corresponding vtk line with the given points
    pvline.cell_data['type'] = [l_type]*pvline.GetNumberOfCells()
    # line.plot()
    appender.AddInputData(pvline) # Add the new object

# Set the RegionId of each line
connectivity = vtkConnectivityFilter()

connectivity.AddInputConnection(appender.GetOutputPort())
connectivity.SetExtractionModeToAllRegions()
connectivity.ColorRegionsOn()

# Fuse overlapping points
clean = vtkCleanPolyData()
clean.AddInputConnection(connectivity.GetOutputPort())
clean.ToleranceIsAbsoluteOn()
clean.SetTolerance(1)
clean.ConvertLinesToPointsOff()
clean.ConvertPolysToLinesOff()
clean.ConvertStripsToPolysOff()
clean.Update()

"""
Once the polydata is defined (with no duplicate points) we can calculate the node adjacency (which node is connected to
a given node) using the networkx library

This library is used to create a node graph and to calculate different properties of such graph but also
enables us to quickly get the adjacency parameter that we need. To create the graph we can use the add_edges_from
function that ingest a [n,2] shaped array where each n row defines an edge of the graph (a pair of linked nodes).

We can obtain such list using the .lines attribute for pyvista objects but the padding needs to be removed.


"""

print('3. Calculating adjacency')


network = pv.wrap(clean.GetOutput())

# Get the backbone

connectivity = vtkConnectivityFilter()

connectivity.AddInputData(network)
connectivity.SetExtractionModeToLargestRegion()

connectivity.Update()

backbone = connectivity.GetOutput()


# Calculate topology
lines = network.lines #Get the connectivity list of the object

lines = np.delete(lines, np.arange(0, lines.size, 3)) # remove padding eg. [2 id1 id2 2 id3 id4 ...] -> remove the 2

nx = net.Graph() # Create a networkx graph instance

nx.add_edges_from(lines.reshape(-1, 2)) # Add the edges

adj_dict = nx.adj # Calculate the adjacency

"""
The result of the adjacency function is a dict-of-dicts where the value for each node is a dictionary of the connected
nodes ({1: {2:{},3:{}},...}). What we need is just the number of nodes connected to the specific node. This is
calculated with the length of the keys for the given key (len(adj_dict[key].keys())).

Once the numbers are defined we can calculate the number of I,Y and X nodes and plot the results. We can also
discriminate between internal and V nodes by:
1. Extracting the cells connected to the given pointid
2. Check if the RegionId of the cells is the same or not. If it is the same then the point is internal

The check is performed using the set function. If the cells are part of the same line (internal node) then the resulting
list will be composed of 1 value (length = 1).
[NOTE] This method could be also used to distinguish T nodes from Y nodes since T nodes should be composed of 2 cells
with the same RegionID and one cell with a different region ID while Y nodes should be characterized by three different
RegionIDs.
"""

print('4. Classifying')


class_id = []

# Create a dict used to translate the numeric values with the classification
class_dict = {
    1: 'I',
    2: 'V',
    3: 'Y',
    4: 'X',
    5: 'U'
}

n_nodes = network.n_points

for i, node in enumerate(adj_dict): # For each node in the dict:
    print(f'Classifying {i}/{n_nodes} nodes', end='\r')
    n_edges = len(adj_dict[node].keys()) # Calculate number of connected nodes
    if n_edges == 2: # Discriminate V and internal nodes
        cells = network.extract_points(node) # Extract the cells
        if len(set(cells['RegionId'])) == 1: # Check if the cellid changes
            n_edges = -9999 # Classify internal nodes
    elif n_edges == 3: # Discriminate Y and U nodes
        cells = network.extract_points(node)
        if 'boundary' in cells.cell_data['type']:
            # print(cells.cell_data['type'])
            net_index = cells.cell_data['RegionId'][np.where(cells.cell_data['type'] != 'boundary')[0]]
            df.loc[net_index, 'U-nodes'] = 1
            n_edges = 5
    elif n_edges > 4:
        n_edges = -9999
    class_id.append(n_edges) # Append the value (number of connected nodes)


# Calculate the necessary info to plot in the ternary classification plot
if class_id.count(1)+class_id.count(3) == 0:
    PI = 0
else:
    PI = 100*class_id.count(1)/(class_id.count(1)+class_id.count(3))

if class_id.count(3)+class_id.count(4) == 0:
    PY = 0
else:
    PY = 100*class_id.count(3)/(class_id.count(3)+class_id.count(4))

if class_id.count(1)+class_id.count(4) == 0:
    PX = 0
else:
    PX = 100*class_id.count(4)/(class_id.count(1)+class_id.count(4))

if class_id.count(1)+class_id.count(5) == 0:
    PU = 0
else:
    PU = 100*class_id.count(5)/(class_id.count(1)+class_id.count(5))

# print(f'I: {PI}')
# print(f'Y: {PY}')
# print(f'X: {PX}')
# print(f'U: {PU}')

"""
To represent the results we can create a pointset and assign to each point the identified adjacency value and filter
such point cloud to remove internal nodes. Also for representation purposes we can translate the number of connections
in the correct classifications (I,V etcetc.).

"""

#Create the pointset
points = pv.PolyData(network.points)
# net.draw(nx, with_labels=True, font_weight='bold')

# Create and assign to each point the number of connected nodes array
points['class_id'] = class_id

# Remove internal nodes (class_id value < 0)
thresh = vtkThreshold()

geom_filter = vtkGeometryFilter()

points.set_active_scalars('class_id')

thresh.AddInputData(points)
thresh.SetLowerThreshold(0)
thresh.InvertOff()
thresh.SetInputArrayToProcess(0, 0, 0, vtkDataObject().FIELD_ASSOCIATION_POINTS, vtkDataSetAttributes().SCALARS)

geom_filter.SetInputConnection(thresh.GetOutputPort())

geom_filter.Update()

filtered = pv.wrap(geom_filter.GetOutput())

# Create a classification list ([I,V,Y,..])
class_names = [class_dict[i] for i in filtered['class_id']]

# Create and assign to each point the correct classification array
filtered['class_tags'] = class_names

# Scalar bar customization for the nodes

sargs = dict(interactive=False,
             vertical=False,
             height=0.1,
             title_font_size=16,
             label_font_size=14)


cmap_dict = {
    'I': 'Blue',
    'V': 'Green',
    'Y': 'Red',
    'X': 'Yellow',
    'U': 'Gray'
}

cmap_dict_lines = {
    'network': 'White',
    'boundary': 'Black'
}
used_tags = list(set(filtered['class_tags']))
used_tags.sort()
cmap = [cmap_dict[i] for i in used_tags]



# Create the ternary plot

figure, tax = ternary.figure(scale=100)
figure.set_size_inches(10, 10)


# Label the corners
tax.right_corner_label("X")
tax.top_corner_label("I")
tax.left_corner_label("Y")
points = [(PX, PI, PY)]

precise_n = 4*(1-PI/100)/(1-PX/100)
# print(precise_n)

# Plot and add the mpl chart to the plotter
tax.scatter(points, marker='o', color='red', label='Classification')
for n in range(8):
    n += 1
    A1 = np.array([[1, 1, 1], [0, 0, 1], [-n, 4, 0]])
    B = np.array([1, 0, 4-n])

    X1 = np.linalg.inv(A1).dot(B)*100
    if n < 4:
        side = [1, 0, 0]
    else:
        side = [0, 1, 0]
    A2 = np.array([[1, 1, 1], side, [-n, 4, 0]])

    X2 = np.linalg.inv(A2).dot(B)*100

    tax.line(X1, X2, color='black', linewidth=1, alpha = n/8)

ax = tax.get_axes()
ax.text(76.8, 21.3, 8)
ax.text(74.8, 23.8, 7)
ax.text(73.5, 27.9, 6)
ax.text(71, 32.3, 5)
ax.text(69.1, 38, 4)
ax.text(65.8, 45, 3)
ax.text(62.7, 54, 2)
ax.text(57, 66.5, 1)

tax.get_axes().set_aspect(1) # This is used to avoid deformation when rescaling the plotter window
tax.clear_matplotlib_ticks()
tax.get_axes().axis('off')

tax.savefig('Ternary_plot.png')


# h_chart = pv.ChartMPL(figure, size=(0.3, 0.3), loc=(0, 0.7))
#
# h_chart.background_color = (1.0, 1.0, 1.0, 0)
# h_chart.border_style = None
#
#
# plotter.add_chart(h_chart)
# Add to the plotter the network mesh
plotter.add_mesh(network,
                 scalars='type',
                 line_width=1,
                 show_scalar_bar=False,
                 cmap=['Red', 'White'])

# Add to the plotter the pointcloud
plotter.add_mesh(filtered,
                 scalars='class_tags',
                 render_points_as_spheres=True,
                 point_size=7,
                 show_scalar_bar=True,
                 scalar_bar_args=sargs,
                 cmap=cmap)
# plotter.subplot(0,1)
# plotter.add_mesh(backbone, color='yellow', line_width=2)

# scale_bar = vtkLegendScaleActor()
#
# plotter.add_actor(scale_bar)

plotter.link_views()
plotter.add_axes()
plotter.view_xy()
plotter.enable_image_style() # lock the view to a 2D image
end = time.time()

print(f'it took: {end - start}s for {total_seg} segments and {n_nodes} found intersection')

report_name = datetime.now().strftime("%d-%m-%Y_%H_%M_%S")

df.loc[df['type'] == 'network'].to_csv(f'{data}_length_dist.csv', columns=['U-nodes', 'length'])

with open(f'{data}_{report_name}.txt', 'w') as o:

    o.write(f'###### Report for {report_name} ######\n\n')
    o.write(f'----------- Input -----------\n\n')
    o.write(f'Input network data: {data}\n')
    o.write(f'Input boundary data: {bound_data}\n\n')
    o.write(f'----------- Output -----------\n\n')
    o.write(f'Run in: {end - start}s\n')
    o.write(f'Number of segments: {total_seg}\n')
    o.write(f'Number of nodes: {n_nodes}\n\n')

    o.write(f'Number of I nodes: {class_id.count(1)} \n')
    o.write(f'Number of Y nodes: {class_id.count(3)} \n')
    o.write(f'Number of X nodes: {class_id.count(4)} \n')
    o.write(f'Number of U nodes: {class_id.count(5)} \n\n')

    o.write(f'I nodes relative %: {PI}\n')
    o.write(f'Y nodes relative %: {PY}\n')
    o.write(f'X nodes relative %: {PX}\n')
    o.write(f'U nodes relative %: {PU}\n\n')

    o.write(f'Mean connections per segment: {precise_n}\n')



plotter.show()












