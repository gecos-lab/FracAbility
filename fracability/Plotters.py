"""
FracAbility has different types of data that needs to be represented in different ways. In the Plotters module
different class adapters are proposed to plot the data. It is possible to plot:


Fracture Network (entity):


1. The geopandas dataframe -> matplotlib:
    + Fractures:
        + Rose plot
        + Backbone(s) -> Different colors if multiple backbones are present
    + Boundary
    + Nodes:
        + Different colors and shapes depending on the node type

2. The VTK entities -> pyvista:
    + Fractures:
        + Backbone(s) -> Different colors if multiple backbones are present
    + Boundary
    + Nodes:
        + Different colors depending on the node type

3. The topology data -> matplotlib:
    + I,Y,X node proportions in a ternary plot

Fracture network (statistics):

1. The statistics -> matplotlib:

    + Single distribution plot (each alone or together):
        + pdf
        + cdf
        + sf
        + summary table

    + Multiple distribution plot:
        + cdf vs ecdf
        + pdf vs histograms
        + P-P and Q-Q plot?


todo the plotters should all inherit from a BasePlotter class
"""
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pyvista import Plotter
import pyvista as pv
import ternary
from fracability.Statistics import NetworkDistribution, NetworkFitter
from fracability.utils.general_use import KM, setFigLinesBW, ecdf_find_x
import numpy as np


def matplot_nodes(entity,
                  markersize=7,
                  return_plot=False,
                  show_plot=True):
    """
    Plot a fracability Nodes entity using matplotlib.

    :param entity: Nodes entity to plot
    :param markersize: Size of the markers as int
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :return: If return_plot is true a matplotlib axis is returned

    Notes
    -------
    The nodes are represented using this color and marker codes:

    1. I nodes: blue red circle
    2. Y nodes: green triangle
    4. X nodes: blue square
    5. U nodes: yellow pentagon
    """

    if 'Fracture net plot' not in plt.get_figlabels():
        figure = plt.figure(num=f'Nodes plot')

        ax = plt.subplot(111)
    else:
        ax = plt.gca()
    vtk_object = entity.vtk_object
    points = vtk_object.points
    node_types = vtk_object['n_type']
    I = np.where(node_types == 1)
    Y = np.where(node_types == 3)
    X = np.where(node_types == 4)
    U = np.where(node_types == 5)

    # todo change the colors to reflect the pallete of the paper
    ax.plot(points[I][:, 0], points[I][:, 1], 'or', markersize=markersize)
    ax.plot(points[Y][:, 0], points[Y][:, 1], '^g', markersize=markersize)
    ax.plot(points[X][:, 0], points[X][:, 1], 'sb', markersize=markersize)
    ax.plot(points[U][:, 0], points[U][:, 1], 'py', markersize=markersize)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def matplot_ternary(entity,
                    return_plot: bool = False,
                    show_plot: bool = True):

    """
    Plot the ternary diagram for nodes

    Parameters
    ----------

    entity: The fracability Nodes entity

    return_plot: Bool. If true return the plot. By default, false

    show_plot: Bool. If true show the plot. By default, true.


    """

    figure, tax = ternary.figure(scale=100)
    figure.set_size_inches(10, 10)

    if entity.name == 'FractureNetwork':
        nodes = entity.nodes
    elif entity.name == 'Nodes':
        nodes = entity

    PI, PY, PX, _, CI = nodes.ternary_node_count
    points = [(PX, PI, PY)]

    tax.scatter(points, marker='o', color='red', label='Classification')
    tax.annotate(f'{np.round(CI,2)}', position=[PX, PI, PY])

    for n in range(8):
        n += 1
        A1 = np.array([[1, 1, 1], [0, 0, 1], [-n, 4, 0]])
        B = np.array([1, 0, 4 - n])

        X1 = np.linalg.inv(A1).dot(B) * 100
        if n < 4:
            side = [1, 0, 0]
        else:
            side = [0, 1, 0]
        A2 = np.array([[1, 1, 1], side, [-n, 4, 0]])

        X2 = np.linalg.inv(A2).dot(B) * 100

        tax.line(X1, X2, color='black', linewidth=1, alpha=n / 8)

    ax = tax.get_axes()
    ax.text(76.8, 21.3, 8)
    ax.text(74.8, 23.8, 7)
    ax.text(73.5, 27.9, 6)
    ax.text(71, 32.3, 5)
    ax.text(69.1, 38, 4)
    ax.text(65.8, 45, 3)
    ax.text(62.7, 54, 2)
    ax.text(57, 66.5, 1)

    tax.right_corner_label("X", fontsize=15)
    tax.top_corner_label("I", fontsize=15)
    tax.left_corner_label("Y", fontsize=15)

    tax.get_axes().set_aspect(1)  # This is used to avoid deformation when rescaling the plotter window
    # tax.clear_matplotlib_ticks()
    tax.get_axes().axis('off')
    if return_plot:
        return tax
    else:
        if show_plot:
            plt.show()


def matplot_fractures(entity,
                      linewidth=1,
                      color='black',
                      color_set=False,
                      return_plot=False,
                      show_plot=True):
    """
    Plot a fracability Fracture entity using matplotlib.

    :param entity: Fracture entity to plot
    :param linewidth: Size of the lines as int
    :param color: General color of the lines as str.
    :param color_set: Bool. If true the lines are based on the set values.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :return: If return_plot is true a matplotlib axis is returned

    """

    if return_plot:
        ax = plt.gca()
    else:
        figure = plt.figure(num=f'Fractures plot')

        ax = plt.subplot(111)

    if color_set:
        if 'f_set' in entity.entity_df.columns:
            n_sets = len(set(entity.entity_df['f_set']))
            cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_sets)
            entity.entity_df.plot(ax=ax,
                                  cmap=cmap,
                                  linewidth=linewidth)
        else:
            return False
    else:

        entity.entity_df.plot(ax=ax, color=color, linewidth=linewidth)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def matplot_boundaries(entity,
                       linewidth=1,
                       color='red',
                       return_plot=False,
                       show_plot=True):
    """
    Plot a fracability Boundary entity using matplotlib.

    :param entity: Boundary entity to plot
    :param linewidth: Size of the lines as int
    :param color: General color of the lines as str
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :return: If return_plot is true a matplotlib axis is returned
    """

    if return_plot:
        ax = plt.gca()
    else:
        figure = plt.figure(num=f'Boundary plot')

        ax = plt.subplot(111)

    entity.entity_df.plot(ax=ax, color=color, linewidth=linewidth)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def matplot_frac_net(entity,
                     markersize=7,
                     fracture_linewidth=1,
                     boundary_linewidth=1,
                     fracture_color='black',
                     boundary_color='red',
                     color_set=False,
                     show_plot=True,
                     return_plot=False):
    """
    Plot a fracability FractureNetwork entity using matplotlib.

    :param entity: FractureNetwork entity to plot
    :param markersize: Size of the nodes
    :param fracture_linewidth: Size of the fracture lines.
    :param boundary_linewidth: Size of the boundary lines.
    :param fracture_color: Color of the fracture lines.
    :param boundary_color: Color of the boundary lines.
    :param color_set: Bool. If true the lines are based on the set values.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :return: If return_plot is true a matplotlib axis is returned

    """
    figure = plt.figure(num=f'Fracture net plot')
    ax = plt.subplot(111)
    nodes = entity.nodes
    fractures = entity.fractures
    boundary = entity.boundaries

    if fractures is not None:
        matplot_fractures(fractures, linewidth=fracture_linewidth,
                          color=fracture_color, color_set=color_set, return_plot=True)
    if boundary is not None:
        matplot_boundaries(boundary, linewidth=boundary_linewidth,
                           color=boundary_color, return_plot=True)
    if nodes is not None:
        matplot_nodes(nodes, markersize=markersize, return_plot=True)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


# todo implement backbone plot with matplotlib
def matplot_backbone(entity,
                     fracture_linewidth=1,
                     boundary_linewidth=1,
                     fracture_color='black',
                     boundary_color='red',
                     color_set=False,
                     show_plot=True,
                     return_plot=False):
    """
    Plot a fracability FractureNetwork entity using matplotlib. (not yet implemented)

    :param entity: FractureNetwork entity to plot
    :param fracture_linewidth: Size of the fracture lines.
    :param boundary_linewidth: Size of the boundary lines.
    :param fracture_color: Color of the fracture lines.
    :param boundary_color: Color of the boundary lines.
    :param color_set: Bool. If true the lines are based on the set values.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :return: If return_plot is true a matplotlib axis is returned

    """
    figure = plt.figure(num=f'Backbone plot')
    ax = plt.subplot(111)

    if 'backbone' in entity.entity_df['type'].values:
        backbone = entity.backbone
    else:
        entity.calculate_backbone()
        backbone = entity.backbone

    boundary = entity.boundaries

    if backbone is not None:
        for bb in backbone:
            matplot_fractures(bb, linewidth=fracture_linewidth,
                              color=fracture_color, color_set=color_set, return_plot=True)
    if boundary is not None:
        matplot_boundaries(boundary, linewidth=boundary_linewidth,
                           color=boundary_color, return_plot=True)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def vtkplot_nodes(entity,
                  markersize=7,
                  return_plot=False,
                  show_plot=True,
                  notebook=True):
    """
    Plot a fracability Nodes entity using vtk.

    :param entity: FractureNetwork entity to plot
    :param markersize: Size of the nodes
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :param notebook: Bool. if true plot using jupyter. By default, True
    :return: If return_plot is true a matplotlib axis is returned

    """
    plotter = Plotter(notebook=notebook)
    plotter.background_color = 'white'
    plotter.view_xy()
    plotter.add_camera_orientation_widget()
    plotter.enable_image_style()

    class_dict = {
        1: 'I',
        2: 'V',
        3: 'Y',
        4: 'X',
        5: 'U',
    }
    cmap_dict = {
        'I': 'Blue',
        'Y': 'Green',
        'X': 'Red',
        'U': 'Yellow'
    }

    nodes = entity.vtk_object

    class_names = [class_dict[int(i)] for i in nodes['n_type']]

    used_tags = list(set(class_names))
    used_tags.sort()
    cmap = [cmap_dict[i] for i in used_tags]

    sargs = dict(interactive=False,
                 vertical=False,
                 height=0.1,
                 title_font_size=16,
                 label_font_size=14)

    actor = plotter.add_mesh(nodes,
                             scalars=class_names,
                             render_points_as_spheres=False,
                             point_size=markersize,
                             show_scalar_bar=True,
                             scalar_bar_args=sargs,
                             cmap=cmap)

    if return_plot:
        return actor
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def vtkplot_fractures(entity,
                      linewidth=1,
                      color='black',
                      color_set=False,
                      return_plot=False,
                      show_plot=True,
                      display_property: str = None,
                      notebook=True):

    """
    Plot a fracability Fracture entity using vtk.

    :param entity: Fracture entity to plot
    :param linewidth: width of the lines
    :param color: General color of the lines as str.
    :param color_set: Bool. If true the fractures are colored using the set.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :param display_property: str. Indicate which property to show. By default, None
    :param notebook: Bool. if true plot using jupyter. By default, True

    :return: If return_plot is true a matplotlib axis is returned

    """

    plotter = Plotter(notebook=notebook)
    plotter.background_color = 'white'
    plotter.view_xy()
    plotter.add_camera_orientation_widget()
    plotter.enable_image_style()

    vtk_object = entity.vtk_object

    if color_set:
        display_property = 'f_set'

    if display_property:

        if display_property in vtk_object.array_names:  # this needs fixin'. Connecting fractures color are "contaminated"
            n_sets = len(set(vtk_object[display_property]))
            cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_sets)
            actor = plotter.add_mesh(vtk_object,
                                     scalars=display_property,
                                     line_width=linewidth,
                                     cmap=cmap,
                                     show_scalar_bar=False)
        else:
            return False
    else:
        actor = plotter.add_mesh(vtk_object,
                                 color=color,
                                 line_width=linewidth,
                                 show_scalar_bar=False)

    if return_plot:
        return actor
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def vtkplot_boundaries(entity,
                       linewidth=1,
                       color='red',
                       return_plot=False,
                       show_plot=True,
                       notebook=True):
    """
    Plot a fracability Boundary entity using vtk.

    :param entity: Fracture entity to plot
    :param linewidth: width of the lines
    :param color: General color of the lines as str.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :param notebook: Bool. if true plot using jupyter. By default, True

    :return: If return_plot is true a matplotlib axis is returned
    """
    plotter = Plotter(notebook=notebook)
    plotter.background_color = 'white'
    plotter.view_xy()
    plotter.add_camera_orientation_widget()
    plotter.enable_image_style()

    actor = plotter.add_mesh(entity.vtk_object,
                     color=color,
                     line_width=linewidth,
                     show_scalar_bar=False)

    if return_plot:
        return actor
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def vtkplot_frac_net(entity,
                     markersize=7,
                     fracture_linewidth=1,
                     boundary_linewidth=1,
                     fracture_color='black',
                     boundary_color='red',
                     color_set=False,
                     show_plot=True,
                     return_plot=False,
                     notebook=True):
    """
    Plot a fracability FractureNetwork entity using Pyvista.



    :param entity: FractureNetwork entity to plot
    :param markersize: Size of the nodes
    :param fracture_linewidth: Size of the fracture lines.
    :param boundary_linewidth: Size of the boundary lines.
    :param fracture_color: Color of the fracture lines.
    :param boundary_color: Color of the boundary lines.
    :param color_set: Bool. If true the lines are based on the set values.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :param notebook: Bool. if true plot using jupyter. By default, True

    :return: If return_plot is true a matplotlib axis is returned

    """
    plotter = Plotter(notebook=notebook)
    plotter.background_color = 'white'
    plotter.view_xy()
    plotter.add_camera_orientation_widget()
    plotter.enable_image_style()

    nodes = entity.nodes
    fractures = entity.fractures
    boundaries = entity.boundaries

    if fractures is not None:
        fractures_actor = vtkplot_fractures(fractures, linewidth=fracture_linewidth,
                                            color=fracture_color, color_set=color_set, return_plot=True)
        plotter.add_actor(fractures_actor)

    if boundaries is not None:
        boundary_actor = vtkplot_boundaries(boundaries, linewidth=boundary_linewidth,
                                            color=boundary_color, return_plot=True)
        plotter.add_actor(boundary_actor)

    if nodes is not None:
        node_actor = vtkplot_nodes(nodes, markersize=markersize, return_plot=True)

        plotter.add_actor(node_actor)

    if return_plot:
        actors = plotter.actors
        return actors
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def vtkplot_backbone(entity,
                     fracture_linewidth=1,
                     boundary_linewidth=1,
                     fracture_color='black',
                     boundary_color='red',
                     return_plot=False,
                     show_plot=True,
                     notebook=True):
    """
    Plot a fracability FractureNetwork backbone entity using pyvista.

    :param entity: FractureNetwork entity to plot
    :param markersize: Size of the nodes
    :param fracture_linewidth: Size of the fracture lines.
    :param boundary_linewidth: Size of the boundary lines.
    :param fracture_color: Color of the fracture lines.
    :param boundary_color: Color of the boundary lines.
    :param color_set: Bool. If true the lines are based on the set values.
    :param return_plot: Bool. If true the plot is returned. By default, False
    :param show_plot: Bool. If true the plot is shown. By default, True
    :param notebook: Bool. if true plot using jupyter. By default, True

    :return: If return_plot is true a matplotlib axis is returned

    """
    plotter = Plotter(notebook=notebook)
    plotter.background_color = 'white'
    plotter.view_xy()
    plotter.add_camera_orientation_widget()
    plotter.enable_image_style()

    if 'backbone' in entity.entity_df['type'].values:
        backbone = entity.backbone
    else:
        entity.calculate_backbone()
        backbone = entity.backbone

    boundaries = entity.boundaries

    if backbone is not None:
        for bb in backbone:
            backbone_actor = vtkplot_fractures(bb, linewidth=fracture_linewidth,
                                               color=fracture_color, return_plot=True)
            plotter.add_actor(backbone_actor)
    if boundaries is not None:
        boundary_actor = vtkplot_boundaries(boundaries, linewidth=boundary_linewidth,
                                            color=boundary_color, return_plot=True)
        plotter.add_actor(boundary_actor)

    if return_plot:
        actors = plotter.actors
        return actors
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def matplot_stats_pdf(network_distribution: NetworkDistribution,
                      histogram: bool = True,
                      show_plot: bool = True):
    """
    Plot PDF and histogram.

    Parameters
    -------
    network_distribution: Input NetworkDistribution object

    histogram: Bool. If true plot also the histogram of the data. By default, is True

    show_plot: Bool. If true show the plot. By default, is True

    """

    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} PDF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.pdf(x_vals)

    plt.plot(x_vals, y_vals, color='r', label=f'{name} pdf')
    if histogram:
        sns.histplot(x_vals, stat='density')

    plt.xlabel('length [m]')
    plt.title('PDF')
    plt.grid(False)
    plt.legend()

    if show_plot:
        plt.show()


def matplot_stats_cdf(network_distribution: NetworkDistribution,
                      plot_ecdf: bool = True,
                      show_plot: bool = True):
    """
    Plot CDF and ECDF.

    Parameters
    -------
    network_distribution: Input NetworkDistribution object

    plot_ecdf: Bool. If true plot also the empirical CDF curve of the data. By default, is True

    show_plot: Bool. If true show the plot. By default, is True

    """

    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} CDF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.cdf(x_vals)

    plt.plot(x_vals, y_vals, color='r', label=f'{name} CDF')
    if plot_ecdf:
        ecdf = network_data.ecdf
        plt.step(x=x_vals, y=ecdf, color='b', label='Empirical CDF', where='post')

    plt.xlabel('length [m]')
    plt.title('CDF')
    plt.grid(True)
    plt.legend()

    if show_plot:
        plt.show()


def matplot_stats_sf(network_distribution: NetworkDistribution,
                     plot_esf: bool = True,
                     show_plot: bool = True):
    """
    Plot SF and ESF.

    Parameters
    -------
    network_distribution: Input NetworkDistribution object

    plot_esf: Bool. If true plot also the empirical SF curve of the data. By default, is True

    show_plot: Bool. If true show the plot. By default, is True

    """
    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} SF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.sf(x_vals)

    plt.plot(x_vals, y_vals, color='r', label=f'{name} SF')
    if plot_esf:
        esf = network_data.esf
        plt.step(x=x_vals, y=esf, color='b', label='Empirical SF', where='post')

    plt.xlabel('length [m]')
    plt.title('SF')
    plt.grid(True)
    plt.legend()

    if show_plot:
        plt.show()


def matplot_stats_table(network_distribution: NetworkDistribution,
                        vertical: bool = True,
                        show_plot: bool = True):
    """
    Plot the stats summary table for both the data and the NetworkDistribution. In particular the following
    estimators are calculated:

        1. Mean
        2. Standard Deviation
        3. Variance
        4. Median
        5. Mode
        6. 5th percentile
        7. 95th percentile
        8. Total number of fractures
        9. % censored

    Parameters
    -----------
    network_distribution: Input NetworkDistribution object

    vertical: Bool. If true the table is vertical (2cols x 7rows). By default, is True

    show_plot: Bool. If true show the plot. By default, is True

    """
    name = network_distribution.distribution_name
    if show_plot:
        fig = plt.figure(num=f'{name} summary table')
        fig.text(0.5, 0.95, f'{name} summary table', ha='center')

    network_data = network_distribution.fit_data
    plt.axis("off")
    dec = 4

    text_mean = f'{np.round(network_distribution.mean, dec)}'
    text_std = f'{np.round(network_distribution.std, dec)}'
    text_var = f'{np.round(network_distribution.var, dec)}'
    text_median = f'{np.round(network_distribution.median, dec)}'
    text_mode = f'{np.round(network_distribution.mode[0], dec)}'
    text_b5 = f'{np.round(network_distribution.b5, dec)}'
    text_b95 = f'{np.round(network_distribution.b95, dec)}'

    text_mean_th = f'{np.round(network_data.mean, dec)}'
    text_std_th = f'{np.round(network_data.std, dec)}'
    text_var_th = f'{np.round(network_data.var, dec)}'
    text_median_th = f'{np.round(network_data.median, dec)}'
    text_mode_th = f'{np.round(network_data.mode[0], dec)}'
    text_b5_th = f'{np.round(network_data.b5, dec)}'
    text_b95_th = f'{np.round(network_data.b95, dec)}'

    text_totalf = f'{network_data.total_n_fractures}'
    text_perc_censor = f'{np.round(network_data.censoring_percentage, dec)}'

    text_AIC_rank = f'{network_distribution.Akaike_rank}'
    text_KS_rank = f'{network_distribution.KS_rank}'
    text_KG_rank = f'{network_distribution.KG_rank}'
    text_AD_rank = f'{network_distribution.AD_rank}'
    text_mean_rank = f'{network_distribution.Mean_rank}'

    general_stats_df = pd.DataFrame(data=[[text_totalf, text_perc_censor]],
                                    columns=['Total number of fractures', '% censored'])

    stats_df = pd.DataFrame(data=[[text_mean_th, text_mean],
                                  [text_median_th, text_median],
                                  [text_mode_th, text_mode],
                                  [text_b5_th, text_b5],
                                  [text_b95_th, text_b95],
                                  [text_std_th, text_std],
                                  [text_var_th, text_var]],
                            columns=['Data', 'Fit'], index=['Mean', 'Median', 'Mode',
                                                            'B5', 'B95', 'Std', 'Var'])

    rank_df = pd.DataFrame(data=[[text_AIC_rank,text_KS_rank, text_KG_rank, text_AD_rank, text_mean_rank]],
                           columns=['Akaike rank', 'KS rank', 'KG rank', 'AD rank', 'Mean rank'])

    if not vertical:
        stats_df = stats_df.transpose()

    gen_table = plt.table(cellText=general_stats_df.values,
                          colLabels=general_stats_df.columns,
                          # colWidths=[0.3, 0.3],
                          loc='upper center',cellLoc='center')

    # gen_table.auto_set_font_size(False)
    # gen_table.auto_set_column_width(col=list(range(len(general_stats_df.columns))))

    sta_table = plt.table(cellText=stats_df.values,
                          rowLabels=stats_df.index,
                          colLabels=stats_df.columns,
                          # colWidths=[0.3, 0.3],
                          loc='center')

    # sta_table.auto_set_font_size(False)
    # sta_table.auto_set_column_width(col=list(range(len(stats_df.columns))))

    ran_table = plt.table(cellText=rank_df.values,
                          colLabels=rank_df.columns,
                          # colWidths=[0.3, 0.3],
                          loc='lower center', cellLoc='center')

    # ran_table.auto_set_font_size(False)
    # ran_table.auto_set_column_width(col=list(range(len(rank_df.columns))))

    if show_plot:
        plt.show()


def matplot_stats_summary(fitter: NetworkFitter,
                          function_list: list = ['pdf', 'cdf', 'sf'],
                          table: bool = True,
                          show_plot: bool = True,
                          position: list = [],
                          sort_by: str = 'Akaike'):
    """
    Summarize PDF, CDF and SF functions and display summary table all
    in a single plot.


    Parameters
    -------
    fitter: Input NetworkFitter object

    function_list: List of function to calculate (cdf, pdf etc.). By default pdf, cdf and sf functions are calculated

    table: Bool. If true the summary table is shown. By default is true

    show_plot: Bool. If true show the plot. By default, is True
    
    position: List.  Plot the models at the given position (1 indexed) in the ordered sorted by the sort_by field. If None show the plots for each fit. By default is [1].

    sort_by: str. If best is True, show the best fit using the indicated column name. By default is Akaike

    """

    # This distribution selection process could be probably optimized
    names = []
    if position:
        for pos in position:
            names.append(fitter.get_fitted_distribution_names(sort_by)[pos-1])
    else:
        names = fitter.get_fitted_distribution_names(sort_by)

    for name in names:
        network_distribution = fitter.get_fitted_distribution(name)
        fig = plt.figure(num=f'{name} summary plot', figsize=(13, 7))
        # fig.text(0.5, 0.02, 'Length [m]', ha='center')
        fig.suptitle(name)
        # fig.text(0.04, 0.5, 'Density', va='center', rotation='vertical')

        for i, func_name in enumerate(function_list):

            if func_name == 'pdf':
                plt.subplot(2, 2, i+1)
                matplot_stats_pdf(network_distribution, show_plot=False)
            if func_name == 'cdf':
                plt.subplot(2, 2, i + 1)
                matplot_stats_cdf(network_distribution, show_plot=False)
            if func_name == 'sf':
                plt.subplot(2, 2, i + 1)
                matplot_stats_sf(network_distribution, show_plot=False)
        if table:
            plt.subplot(2, 2, i+2)
            plt.axis("off")
            plt.ylim([0, 8])
            plt.xlim([0, 10])
            matplot_stats_table(network_distribution, show_plot=False)

            plt.tight_layout()

        if show_plot:
            plt.show()


def matplot_stats_uniform(fitter: NetworkFitter,
                          show_plot: bool = True,
                          position: list = None,
                          sort_by: str = 'Akaike',
                          bw: bool = False,
                          second_axis: bool = True,
                          n_ticks: int = 5):
    """
    Confront the fitted data with the standard uniform 0,1. Following Kim 2019

    Parameters
    -------
    fitter: Input NetworkFitter object

    show_plot: Bool. If true show the plot. By default, is True

    position: List.  Plot the models at the given position (1 indexed) in the ordered fit_records dataframe sorted by the sort_by field. If None show the plots for each fit. Default is None

    sort_by: str. If best is True, show the best fit using the indicated column name. By default is Akaike

    bw: Bool. If true turn the plot color-blind friendly (black lines with different patterns). Max 7 lines (i.e. models). Default is False

    second_axis: Bool. If true plot the secondary X axis representing the corresponding values of the cumulative in meters. Default is True

    n_ticks: int. Number of ticks on the second axis.

    todo add custom second axis values
    """

    delta = fitter.network_data.delta
    ecdf = fitter.network_data.ecdf
    samples = fitter.network_data.lengths

    # This distribution selection process could be probably optimized
    names = []
    if position:
        for pos in position:
            names.append(fitter.get_fitted_distribution_names(sort_by)[pos-1])
    else:
        names = fitter.get_fitted_distribution_names(sort_by)

    fig = plt.figure(num=f'Comparison plot', figsize=(13, 7))
    ax = plt.subplot(111)

    for name in names:
        network_distribution = fitter.get_fitted_distribution(name)
        Z = network_distribution.cdf()
        G_n = KM(Z, Z, delta)  # not sure about this!
        ax.plot(Z, G_n, label=f'{name}')

    if bw:
        setFigLinesBW(fig)

    if second_axis:
        x_ticks = np.linspace(0, 1, n_ticks)

        xticks_labels = ecdf_find_x(samples=samples, ecdf_prob=ecdf, y_values=x_ticks)

        ax2 = ax.twiny()
        ax2.plot(x_ticks, [0] * len(x_ticks), visible=False)
        ax2.spines['top'].set_position(('axes', -0.11))
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_position(('axes', -0.05))
        ax2.spines['bottom'].set_visible(True)
        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(xticks_labels)

        ax2.annotate(f'Reference length [m]', (-0.01, 0.5), ha='right', va='center', xycoords=ax2.spines['bottom'])

        plt.tick_params(which='both', direction='inout', bottom=True, top=False, length=6)

    if show_plot:
        ax.plot([0, 1], [0, 1], color='r', label='U (0,1)')
        ax.grid(False)
        ax.legend()
        plt.title('Distance to Uniform comparison')
        plt.show()


def matplot_tick_plot(fitter: NetworkFitter,
                      show_plot: bool = True,
                      position: list = None,
                      n_ticks: int = 5,
                      sort_by: str = 'Akaike'):
    """
    Plot the tick plot of the fitted models. (Describe the tick plot).
    :param position:
    :param n_ticks:
    :param fitter:
    :param show_plot:
    :param sort_by:
    :return:
    """

    names = []
    if position:
        for pos in position:
            names.append(fitter.get_fitted_distribution_names(sort_by)[pos-1])
    else:
        names = fitter.get_fitted_distribution_names(sort_by)

    fig = plt.figure(num=f'Tick plot', figsize=(13, 7))
    ax = plt.subplot(111)

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()

    samples = fitter.network_data.lengths
    ecdf = fitter.network_data.ecdf

    x_ticks = np.linspace(0, 1, n_ticks)

    xticks_labels = ecdf_find_x(samples=samples, ecdf_prob=ecdf, y_values=x_ticks)

    for i, name in enumerate(names):
        network_distribution = fitter.get_fitted_distribution(name)
        y = i
        plt.axhline(y=y, color='k')
        values_labels = network_distribution.cdf(xticks_labels)
        for value, x in zip(values_labels, xticks_labels):
            point = ax.plot(value, y, 'k|', markersize=12, linewidth=1)
            ax.annotate(xy=(0.5, -1.1), text=f'{x}', ha='center', va='center', xycoords=point[0], annotation_clip=True)

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(bottom=-0.5)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(xticks_labels)
    ax.set_xlabel('Length[m]')
    ax.annotate(f'Kaplan-Meier', (-0.01, 0.5), ha='right', va='center', xycoords=ax.spines['bottom'])

    ax.grid('y')
    ax.spines[['left', 'top', 'right']].set_visible(False)

    if show_plot:
        plt.title('Tick plot')
        plt.show()