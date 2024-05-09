import scooby
import pyperclip
import numpy as np
import pyvista as pv


def report():
    """ Method used to create a report using scooby and copy it in the clipboard"""
    core = ['fracability', 'pyvista', 'vtk', 'numpy', 'geopandas', 'shapely']
    text = scooby.Report(core=core, ncol=3, text_width=80, sort=True, additional=None, optional=None)
    print(text)
    pyperclip.copy(str(text))
    print('Report copied to clipboard')


def centers_to_lines(center_coords, lengths, frac_dir, assign_id=True) -> pv.PolyData:
    """ Function used to create fractures of given lengths from center coordinates.

    :param center_coords: xyz coordinate centers array of the fractures
    :param lengths: length array for each fracture.
    :param frac_dir: direction array of each fracture.
    :param assign_id: Flag used to assign the id of each fracture as a field (RegionId). Default True

    :return: Pyvista polydata with the same number of fracture as centers.
    """

    half_lengths = lengths/2
    xyz1 = center_coords.copy()
    xyz2 = center_coords.copy()

    xyz1[:, 0] = center_coords[:, 0] + half_lengths * np.sin(np.deg2rad(frac_dir))
    xyz2[:, 0] = center_coords[:, 0] + half_lengths * np.sin(np.deg2rad((frac_dir + 180) % 360))

    xyz1[:, 1] = center_coords[:, 1] + half_lengths * np.cos(np.deg2rad(frac_dir))
    xyz2[:, 1] = center_coords[:, 1] + half_lengths * np.cos(np.deg2rad((frac_dir + 180) % 360))

    xyz_complete = np.array([[i, j] for i, j in zip(xyz1, xyz2)]).reshape(-1, 3)
    conn = np.insert(np.arange(0, len(xyz_complete)), np.arange(0, len(xyz_complete), 2), 2)
    lines = pv.PolyData(xyz_complete, lines=conn)

    if assign_id:
        regions_ids = np.arange(0, len(center_coords))
        lines['RegionId'] = regions_ids

    return lines


def KM(z_values, Z, delta_list):

    """
    Calculate the Kaplan-Meier curve given an input z, data Z and list of deltas.
    :param z_values: Input
    :param Z: Data (sorted)
    :param delta_list: list of deltas (sorted as Z)
    :return:
    """

    def p_cap(n, j_index, d_list):
        """
        Calculate the ^p estimator (formula 2.6)
        :param n: total number
        :param j_index: index list
        :param d_list: delta list
        :return:
        """
        product = 1  # initiate product as 1 (so that the first step p1 will be product=p1

        for j in j_index:  # for each index in the index list
            d = d_list[j]
            real_j = j + 1
            p = ((n - real_j) / (n - real_j + 1)) ** d
            product *= p

        return 1 - product

    # Sort Z in case it is not sorted at input (also delta_list needs to be sorted in the same order of Z)
    sorted_args = np.argsort(Z)
    Z_sort = Z[sorted_args]
    delta_list_sort = delta_list[sorted_args]

    G = np.ones_like(z_values)
    n = len(Z)

    for i, z in enumerate(z_values):
        if z < Z_sort[0]:
            G[i] = 0
        elif z <= Z_sort[-1]:
            j_index = np.where(Z_sort <= z)[0]  # Get the index in which the data Z is lower than z
            G[i] = p_cap(n, j_index, delta_list_sort)  # Calculate the p_cap
        elif z > Z_sort[-1]:
            G[i] = 1

    return G


def setAxLinesBW(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be
    suitable for black and white viewing.
    Code taken from https://stackoverflow.com/questions/7358118/black-white-colormap-with-dashes-dots-etc
    """
    MARKERSIZE = 1

    COLORMAP = [{'marker': '', 'dash': (None, None)},
                {'marker': '', 'dash': [5, 5]},
                {'marker': '', 'dash': [5, 3, 1, 3]},
                {'marker': '', 'dash': [1, 3]},
                {'marker': '', 'dash': [5, 2, 5, 2, 5, 10]},
                {'marker': '', 'dash': [5, 3, 1, 2, 1, 10]},
                {'marker': '', 'dash': [1, 2, 1, 10]}
                ]

    lines_to_adjust = ax.get_lines()
    try:
        lines_to_adjust += ax.get_legend().get_lines()
    except AttributeError:
        pass

    for i, line in enumerate(lines_to_adjust):
        line.set_color('black')
        line.set_dashes(COLORMAP[i]['dash'])
        line.set_marker(COLORMAP[i]['marker'])
        line.set_markersize(MARKERSIZE)


def setFigLinesBW(fig):

    """
    Take each axes in the figure, and for each line in the axes, make the
    line viewable in black and white.
    Code taken from https://stackoverflow.com/questions/7358118/black-white-colormap-with-dashes-dots-etc
    """
    for ax in fig.get_axes():
        setAxLinesBW(ax)