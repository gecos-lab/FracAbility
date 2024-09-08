import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import pandas as pd
import seaborn as sns

import sys
import numpy
numpy.set_printoptions(threshold=sys.maxsize)


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
        real_j = j+1
        p = ((n-real_j)/(n-real_j+1))**d
        product *= p

    return 1-product


def KM(z_values, Z, delta_list):

    """
    Calculate the Kaplan-Meier curve given an input z, data Z and list of deltas.
    :param z_values: Input
    :param Z: Data (sorted)
    :param delta_list: list of deltas (sorted as Z)
    :return:
    """
    # Sort Z in case it is not sorted at input (also delta_list needs to be sorted in the same order of Z)
    if delta_list is None:
        delta_list = np.ones_like(z_values)

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


data = pd.read_csv('Pontrelli/Pontrelli_out/output/csv/Fractures_1.csv', index_col=0, sep=';')


data = data.sort_values(by='length')  # sort the data by length

lengths = data['length'].values  # Length value

lengths = lengths[lengths != np.nan]

censored_value = data['censored'].values  # Censoring values: 0 is complete, 1 is censored
delta = 1-censored_value  # In the formulas delta = 1 means complete while 0 means censored.

tot_n = len(lengths)

censored = data.loc[censored_value == 1, 'length'].values  # Extract only the censored values
uncensored = data.loc[censored_value == 0, 'length'].values  # Extract only the complete values

censoring_percentage = 100*len(censored)/tot_n

data_cens = ss.CensoredData(uncensored, right=censored)  # Create the scipy CensoredData instance

name = 'lognorm'
dist = getattr(ss, name)

ignore_censoring = dist.freeze(*dist.fit(lengths, floc=0))
remove_censored = dist.freeze(*dist.fit(uncensored, floc=0))
survival = dist.freeze(*dist.fit(data_cens, floc=0))

df = pd.DataFrame()

df['mean'] = np.round([ignore_censoring.mean(),
                      remove_censored.mean(),
                      survival.mean()], 3)

df['std'] = np.round([ignore_censoring.std(),
                      remove_censored.std(),
                      survival.std()], 3)

df['model'] = ['Ignore censoring', 'Remove censored', 'Survival']
df.set_index('model', inplace=True)

df.to_clipboard(excel=True)

Z_ignore = ignore_censoring.cdf(lengths)
Z_remove = remove_censored.cdf(lengths)
Z_survival = survival.cdf(lengths)

fig = plt.figure(num=f'PIT', figsize=(13, 7))
plt.annotate(f'Censoring percentage: {censoring_percentage :.2f}%', (0.75, 0.14), va='top',
             ha='left', fontsize='large', xycoords='figure fraction')


gn_ignore = KM(Z_ignore, Z_ignore, delta)
gn_remove = KM(Z_remove, Z_remove, delta)
gn_survival = KM(Z_survival, Z_survival, delta)

plt.plot(Z_ignore, gn_ignore, label='PIT ignore', drawstyle='steps')
plt.plot(Z_remove, gn_remove, label='PIT remove', drawstyle='steps')
plt.plot(Z_survival, gn_survival, label='PIT survival', drawstyle='steps')

setFigLinesBW(fig)
plt.plot([0, 1], [0, 1], label='U (0,1)', color='red')
plt.title('Uniform comparison')
plt.legend()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()
plt.show()