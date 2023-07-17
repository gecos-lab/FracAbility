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

"""
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pyvista import Plotter
import ternary
from fracability.operations.Statistics import NetworkDistribution
import numpy as np


def matplot_nodes(entity, markersize=7, return_plot=False, show_plot=True):

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
    Y2 = np.where(node_types == 6)

    ax.plot(points[I][:, 0], points[I][:, 1], 'or', markersize=markersize)
    ax.plot(points[Y][:, 0], points[Y][:, 1], '^g', markersize=markersize)
    ax.plot(points[Y2][:, 0], points[Y2][:, 1], '^c', markersize=markersize)
    ax.plot(points[X][:, 0], points[X][:, 1], 'sb', markersize=markersize)
    ax.plot(points[U][:, 0], points[U][:, 1], 'py', markersize=markersize)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def matplot_fractures(entity, linewidth=1, color='black', color_set=False, return_plot=False, show_plot=True):

    if 'Fracture net plot' not in plt.get_figlabels():
        figure = plt.figure(num=f'Fractures plot')

        ax = plt.subplot(111)
    else:
        ax = plt.gca()

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


def matplot_boundaries(entity, linewidth=1, color='black', return_plot=False, show_plot=True):

    if 'Fracture net plot' not in plt.get_figlabels():
        figure = plt.figure(num=f'Boundaries plot')

        ax = plt.subplot(111)
    else:
        ax = plt.gca()

    entity.entity_df.plot(ax=ax, color=color, linewidth=linewidth)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def matplot_frac_net(entity, markersize=5, linewidth=[2, 2],
                     color=['black', 'blue'], color_set=False, return_plot=False, show_plot=True):

    figure = plt.figure(num=f'Fracture net plot')
    ax = plt.subplot(111)
    nodes = entity.nodes
    fractures = entity.fractures
    boundary = entity.boundaries

    if fractures is not None:
        matplot_fractures(fractures, linewidth=linewidth[0], color=color[0], color_set=color_set, return_plot=True)
    if boundary is not None:
        matplot_boundaries(boundary, linewidth=linewidth[1], color=color[1], return_plot=True)
    if nodes is not None:
        matplot_nodes(nodes, markersize=markersize, return_plot=True)

    if return_plot:
        return ax
    else:
        if show_plot:
            plt.show()


def vtkplot_nodes(entity, markersize=7, return_plot=False, show_plot=True):

    plotter = Plotter()
    plotter.view_xy()
    plotter.enable_image_style()

    class_dict = {
        1: 'I',
        2: 'V',
        3: 'Y',
        4: 'X',
        5: 'U',
        6: 'Y2'
    }
    cmap_dict = {
        'I': 'Blue',
        'Y': 'Green',
        'Y2': 'Cyan',
        'X': 'Red',
        'U': 'Yellow'
    }

    nodes = entity.vtk_object

    class_names = [class_dict[i] for i in nodes['n_type']]

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
                             render_points_as_spheres=True,
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
                      color='white',
                      color_set=False,
                      return_plot=False,
                      show_plot=True,
                      display_property: str = None):

    print(display_property)
    plotter = Plotter()
    plotter.view_xy()
    plotter.enable_image_style()

    vtk_object = entity.vtk_object

    if color_set:
        display_property = 'f_set'

    if display_property:
        print(display_property)
        if display_property in vtk_object.array_names:
            n_sets = len(set(vtk_object[display_property]))
            cmap = matplotlib.colormaps.get_cmap("rainbow").resampled(n_sets)
            actor = plotter.add_mesh(entity.vtk_object, #this needs fixin'. Connecting fractures color are "contaminated"
                                     scalars=display_property,
                                     line_width=linewidth,
                                     cmap=cmap,
                                     show_scalar_bar=False)
        else:
            return False
    else:

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


def vtkplot_boundaries(entity, linewidth=1, color='white', return_plot=False, show_plot=True):

    plotter = Plotter()
    plotter.view_xy()
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


def vtkplot_frac_net(entity, markersize=5, linewidth=[2, 2],
                     color=['white', 'white'], color_set=False, return_plot=False, show_plot=True):

    plotter = Plotter()
    plotter.view_xy()
    plotter.enable_image_style()

    nodes = entity.nodes
    fractures = entity.fractures
    boundaries = entity.boundaries

    if nodes is not None:
        node_actor = vtkplot_nodes(nodes, markersize=markersize, return_plot=True)
        plotter.add_actor(node_actor)

    if fractures is not None:
        fractures_actor = vtkplot_fractures(fractures, linewidth=linewidth[0],
                                            color=color[0], color_set=color_set, return_plot=True)
        plotter.add_actor(fractures_actor)

    if boundaries is not None:
        boundary_actor = vtkplot_boundaries(boundaries, linewidth=linewidth[1], color=color[1], return_plot=True)
        plotter.add_actor(boundary_actor)

    if return_plot:
        actors = plotter.actors
        return actors
    else:
        if show_plot:
            plotter.reset_camera()
            plotter.show()


def matplot_stats_pdf(network_distribution: NetworkDistribution, histogram: bool = True, show_plot=True):
    sns.set_theme()
    """
    Plot PDF and histogram.

    Parameters
    -------
    x_min: Lower value of the range. By default is set to 0

    x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

    res: Point resolution between x_min and x_max. By default is set to 1000

    """

    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} PDF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.pdf(x_vals)

    sns.lineplot(x=x_vals, y=y_vals, color='r', label=f'{name} pdf')
    if histogram:
        sns.histplot(x_vals, stat='density', bins=50)

    plt.xlabel('length [m]')
    plt.title('PDF')
    plt.grid(True)
    plt.legend()

    # if table:
    #     plt.subplot(2, 1, 2)
    #     matplot_stats_table(network_distribution)

    # cellText = [[text_mean_th, text_median_th, text_mode_th, text_b5_th, text_b95_th, text_std_th, text_var_th],
    #             [text_mean, text_median, text_mode, text_b5, text_b95, text_std, text_var]],
    if show_plot:
        plt.show()


def matplot_stats_cdf(network_distribution: NetworkDistribution, plot_ecdf: bool = True, show_plot: bool = True):
    sns.set_theme()
    """
    Plot CDF and ECDF.

    Parameters
    -------
    x_min: Lower value of the range. By default is set to 0

    x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

    res: Point resolution between x_min and x_max. By default is set to 1000

    """

    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} CDF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.cdf(x_vals)

    sns.lineplot(x=x_vals, y=y_vals, color='r', label=f'{name} CDF')
    if plot_ecdf:
        ecdf = network_data.ecdf
        sns.lineplot(x=ecdf.quantiles, y=ecdf.probabilities, color='b', label='Empirical CDF')

    plt.xlabel('length [m]')
    plt.title('CDF')
    plt.grid(True)
    plt.legend()

    # if table:
    #     plt.subplot(2, 1, 2)
    #     matplot_stats_table(network_distribution)

    # cellText = [[text_mean_th, text_median_th, text_mode_th, text_b5_th, text_b95_th, text_std_th, text_var_th],
    #             [text_mean, text_median, text_mode, text_b5, text_b95, text_std, text_var]],
    if show_plot:
        plt.show()


def matplot_stats_sf(network_distribution: NetworkDistribution, plot_esf: bool = True, show_plot: bool = True):
    sns.set_theme()
    """
    Plot SF and ESF.

    Parameters
    -------
    x_min: Lower value of the range. By default is set to 0

    x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

    res: Point resolution between x_min and x_max. By default is set to 1000

    """

    distribution = network_distribution.distribution
    name = network_distribution.distribution_name

    network_data = network_distribution.fit_data

    x_vals = network_data.lengths

    if show_plot:
        fig = plt.figure(num=f'{name} SF plot', figsize=(13, 7))
        fig.text(0.5, 0.95, name, ha='center')

    y_vals = distribution.sf(x_vals)

    sns.lineplot(x=x_vals, y=y_vals, color='r', label=f'{name} SF')
    if plot_esf:
        esf = network_data.esf
        sns.lineplot(x=esf.quantiles, y=esf.probabilities, color='b', label='Empirical SF')

    plt.xlabel('length [m]')
    plt.title('SF')
    plt.grid(True)
    plt.legend()

    if show_plot:
        plt.show()


def matplot_stats_table(network_distribution: NetworkDistribution, vertical: bool = True, show_plot: bool = True):

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

    stats_df = pd.DataFrame(data=[[text_mean_th, text_mean],
                                  [text_median_th, text_median],
                                  [text_mode_th, text_mode],
                                  [text_b5_th, text_b5],
                                  [text_b95_th, text_b95],
                                  [text_std_th, text_std],
                                  [text_var_th, text_var]],
                            columns=['Data', 'Fit'], index=['Mean', 'Median', 'Mode',
                                                            'B5', 'B95', 'Std', 'Var'])
    if not vertical:
        stats_df = stats_df.transpose()

    plt.table(cellText=stats_df.values,
              rowLabels=stats_df.index,
              colLabels=stats_df.columns,
              # colWidths=[0.3, 0.3],
              loc='center')

    if show_plot:
        plt.show()


def matplot_stats_summary(network_distribution: NetworkDistribution, function_list: list = ['pdf', 'cdf', 'sf'],
                          table=True, show_plot: bool = True):
    sns.set_theme()
    """
    Summarize PDF, CDF and SF functions and display mean, std, var, median, mode, 5th and 95th percentile all
    in a single plot.
    A range of values and the resolution can be defined with the x_min, x_max and res parameters.

    Parameters
    -------
    x_min: Lower value of the range. By default is set to 0

    x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default

    res: Point resolution between x_min and x_max. By default is set to 1000

    """

    name = network_distribution.distribution_name

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


def matplot_ternary(entity, return_plot:bool = False, show_plot: bool = True ):

    """
    Plot the ternary diagram for nodes
    :param entity:
    """

    figure, tax = ternary.figure(scale=100)
    figure.set_size_inches(10, 10)

    if entity.name == 'FractureNetwork':
        nodes = entity.nodes
    elif entity.name == 'Nodes':
        nodes = entity

    PI, PY, PX = nodes.node_count[: 3]
    points = [(PX, PI, PY)]

    tax.scatter(points, marker='o', color='red', label='Classification')

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



