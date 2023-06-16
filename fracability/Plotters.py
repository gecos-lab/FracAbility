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

import matplotlib.pyplot as plt
import seaborn as sns
from pyvista import Plotter
import ternary
from fracability.Entities import BaseEntity
from fracability.operations.Statistics import AbstractStatistics
import numpy as np


def matplot_entity(entity: BaseEntity, markersize=5):

    """
    Plot the given entity using matplotlib
    :param markersize:
    :param entity:
    :return:
    """

    name = entity.__class__.__name__

    figure = plt.figure(num=f'{name} plot')

    ax = plt.subplot(111)

    if name == 'Nodes':

        points = entity.vtk_object.points
        node_types = entity.vtk_object['node_type']
        I = np.where(node_types == 1)
        Y = np.where(node_types == 3)
        X = np.where(node_types == 4)
        U = np.where(node_types == 5)

        ax.plot(points[I][:, 0], points[I][:, 1], 'or', markersize=markersize)
        ax.plot(points[Y][:, 0], points[Y][:, 1], '^g', markersize=markersize)
        ax.plot(points[X][:, 0], points[X][:, 1], 'sb', markersize=markersize)
        ax.plot(points[U][:, 0], points[U][:, 1], 'py', markersize=markersize)

    elif name == 'Fractures':
        entity.entity_df.plot(ax=ax, color='black')

    elif name == 'Boundary':
        entity.entity_df.plot(ax=ax, color='blue')
    else:
        nodes = entity.nodes
        fractures = entity.fractures
        boundaries = entity.boundaries

        points = nodes.vtk_object.points
        node_types = nodes.vtk_object['node_type']
        I = np.where(node_types == 1)
        Y = np.where(node_types == 3)
        X = np.where(node_types == 4)
        U = np.where(node_types == 5)

        fractures.entity_df.plot(ax=ax, color='black')
        boundaries.entity_df.plot(ax=ax, color='blue')
        ax.plot(points[I][:, 0], points[I][:, 1], 'ob', markersize=markersize)
        ax.plot(points[Y][:, 0], points[Y][:, 1], '^g', markersize=markersize)
        ax.plot(points[X][:, 0], points[X][:, 1], 'sr', markersize=markersize)
        ax.plot(points[U][:, 0], points[U][:, 1], 'py', markersize=markersize)

    plt.show()


def plot_vtk_entity(entity: BaseEntity, pointsize=7):

    """
    Plot the given entity using vtk
    :param pointsize:
    :param entity:
    :return:
    """

    name = entity.__class__.__name__

    plotter = Plotter()

    class_dict = {
        1: 'I',
        2: 'V',
        3: 'Y',
        4: 'X',
        5: 'U'
    }
    cmap_dict = {
        'I': 'Blue',
        'Y': 'Green',
        'X': 'Red',
        'U': 'Yellow'
    }


    if name == 'Nodes':

        nodes = entity.vtk_object

        class_names = [class_dict[i] for i in nodes['node_type']]

        used_tags = list(set(class_names))
        used_tags.sort()
        cmap = [cmap_dict[i] for i in used_tags]

        sargs = dict(interactive=False,
                     vertical=False,
                     height=0.1,
                     title_font_size=16,
                     label_font_size=14)

        plotter.add_mesh(nodes,
                         scalars=class_names,
                         render_points_as_spheres=True,
                         point_size=pointsize,
                         show_scalar_bar=True,
                         scalar_bar_args=sargs,
                         cmap=cmap)

    elif name == 'Fractures':
        plotter.add_mesh(entity.vtk_object,
                         color='white',
                         line_width=1,
                         show_scalar_bar=False)
    elif name == 'Boundaries':
        plotter.add_mesh(entity.vtk_object,
                         color='blue',
                         line_width=1,
                         show_scalar_bar=False)

    else:
        nodes = entity.nodes.vtk_object
        fractures = entity.fractures.vtk_object
        boundaries = entity.boundaries.vtk_object

        class_names = [class_dict[i] for i in nodes['node_type']]

        used_tags = list(set(class_names))
        used_tags.sort()
        cmap = [cmap_dict[i] for i in used_tags]

        sargs = dict(interactive=False,
                     vertical=False,
                     height=0.1,
                     title_font_size=16,
                     label_font_size=14)

        plotter.add_mesh(fractures,
                         color='white',
                         line_width=1,
                         show_scalar_bar=False)
        plotter.add_mesh(boundaries,
                         color='white',
                         line_width=1,
                         show_scalar_bar=False)

        plotter.add_mesh(nodes,
                         scalars=class_names,
                         render_points_as_spheres=True,
                         point_size=pointsize,
                         show_scalar_bar=True,
                         scalar_bar_args=sargs,
                         cmap=cmap)
    plotter.show()


def matplot_stats_summary(fitter: AbstractStatistics, x_min: float = 0.0, x_max: float = None, res: int = 200):
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

    if x_max is None:
        x_max = max(fitter.lengths)

    cdf = fitter.ecdf.cdf
    x_vals = cdf.quantiles

    fit_rec = fitter.fit_records

    for index, line in fit_rec.iterrows():

        dist = line['distribution']
        name = line['name']
        aicc = line['AICc']
        bic = line['BIC']
        ll = line['log_likelihood']

        params = fitter.get_fit_parameters(name)

        fig = plt.figure(num=f'{name} summary plot', figsize=(13, 7))
        fig.text(0.5, 0.02, 'Length [m]', ha='center')
        fig.text(0.5, 0.95, name, ha='center')
        fig.text(0.04, 0.5, 'Density', va='center', rotation='vertical')

        for i, func_name in enumerate(fitter.function_list[:3]):
            func = getattr(dist, func_name)

            y_vals = func(x_vals, *params)

            plt.subplot(2, 2, i+1)

            sns.lineplot(x=x_vals, y=y_vals, color='r', label=f'{name} {func_name}')

            if func_name == 'pdf':
                sns.histplot(fitter.lengths, stat='density', bins=50)
            if func_name == 'cdf':
                sns.lineplot(x=x_vals, y=cdf.probabilities, color='b', label='Empirical CDF')

            plt.title(func_name)
            plt.grid(True)
            plt.legend()

        plt.subplot(2, 2, i+2)
        plt.axis("off")
        plt.ylim([0, 8])
        plt.xlim([0, 10])
        dec = 4

        text_mean = f'Mean = {np.round(dist.mean(*params), 3)}'
        text_std = f'Std = {round(dist.std(*params), 3)}'
        text_var = f'Var = {round(dist.var(*params), 3)}'
        text_median = f'Median = {round(dist.median(*params), 3)}'
        # text_mode = f'Mode = {round(dist.mode(*params), 3)}'
        # text_b5 = f'5th Percentile = {round(dist.b5(*params), 3)}'
        # text_b95 = f'95th Percentile = {round(dist.b95(*params), 3)}'

        plt.text(0, 7.5, 'Summary table')
        plt.text(0, 6.5, text_mean)
        plt.text(0, 5.5, text_median)
        # plt.text(0, 4.5, text_mode)
        # plt.text(0, 3.5, text_b5)
        # plt.text(0, 2.5, text_b95)
        plt.text(0, 1.5, text_std)
        plt.text(0, 0.5, text_var)

        plt.text(6, 7.5, 'Test results:')

        text_result = f'AICc value = {np.round(aicc, 3)}'
        text_crit_val = f'BIC value = {np.round(bic, 3)}'
        text_ks_val = f'Log Likelihood value = {np.round(ll, 3)}'

        plt.text(6, 6.5, text_result)
        plt.text(6, 5.5, text_crit_val)
        plt.text(6, 4.5, text_ks_val)

    plt.show()


def matplot_ternary(entity: BaseEntity):

    """
    Plot the ternary diagram for nodes
    :param entity: 
    :return: 
    """
    name = entity.__class__.__name__
    figure, tax = ternary.figure(scale=100)
    figure.set_size_inches(10, 10)

    if name == 'FractureNetwork':
        nodes = entity.nodes
    elif name == 'Nodes':
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
    tax.clear_matplotlib_ticks()
    tax.get_axes().axis('off')

    plt.show()


