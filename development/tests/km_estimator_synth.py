import matplotlib.pyplot as plt
import numpy as np
from numpy import exp
from numpy import log as ln
import scipy.stats as ss
import pandas as pd

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



# names = ['lognorm', 'gengamma', 'expon', 'weibull_min', 'norm', 'burr12']  # list of names of scipy distribution to test
data_frame = pd.DataFrame(columns=['dist_name',
                                   'AIC', 'delta_i', 'w_i',
                                   'KS', 'KG', 'AD',
                                   'AIC rank', 'KS rank', 'KG rank', 'AD rank', 'Mean rank'], dtype=float)  # Create empty final dataframe

data_frame['dist_name'] = data_frame['dist_name'].astype(str)

tot_n = 1000
samples = np.random.normal(size=tot_n)
delta = np.ones(len(samples))
samples.sort()
mu = np.arange(-2, 3, 2)
exp_dist = ss.expon(scale=1)
log_dist = ss.lognorm(loc=0, s=1)

smallest_number = np.finfo(np.float64).tiny


ecdf = KM(samples, samples, delta)
model_dict = {}

for m in mu:
    dist = ss.norm(m, 1)
    model_dict[dist] = f'N ({m}, 1)'

model_dict[exp_dist] = f'E(1)'
model_dict[log_dist] = f'Ln(0, 1)'


for i, dist in enumerate(model_dict.keys()):  # for each scipy distribution do:
    fitted_dist = dist
    name = model_dict[dist]
    print(name)
    data_frame.loc[i, 'dist_name'] = name
    loc_list = ['norm', 'logistic']  # list of dist names that have only two parameters (and so floc must not be set to 0)



    # Akaike 1974

    max_like = fitted_dist.logpdf(samples).sum()
    k = len(fitted_dist.args) # because floc is fixed to 0, it is not considered in the maximum likelihood and so the number of optimized arguments of the distribution are - 1
    AIC = (-2*max_like)+(2*k)
    data_frame.loc[i, 'AIC'] = AIC

    # Kim 2019

    Z = fitted_dist.cdf(samples)
    G_n = KM(Z, Z, delta)
    plt.plot(Z, G_n, label=f'G_n {name}')  # plot the Kaplan-Meier curves with steps.

    ## Kolmogorov-Smirnov test

    complete_list_index = np.where(delta == 1)[0]

    diff_plus_list = []
    diff_minus_list = []

    for j in complete_list_index:
        diff_plus = G_n[j]-Z[j]  # Calculate the positive difference at index j (DC+)

        if j+1 > tot_n-1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
            Z_j1 = 1
        else:
            Z_j1 = Z[j+1]

        diff_minus = Z_j1-G_n[j]  # Calculate the negative difference at index j (DC-)
        diff_plus_list.append(diff_plus)
        diff_minus_list.append(diff_minus)

    DCn_pos = max(diff_plus_list)
    DCn_neg = max(diff_minus_list)

    DCn = max(DCn_pos, DCn_neg)

    data_frame.loc[i, 'KS'] = DCn

    ## Koziol and Green test

    kg_sum = 0

    for j in range(tot_n):

        if j+1 > tot_n-1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
            Z_j1 = 1
        else:
            Z_j1 = Z[j+1]
        kg_sum += G_n[j]*(Z_j1-Z[j])*(G_n[j]-(Z_j1+Z[j]))

    psi_sq = (tot_n*kg_sum)+tot_n/3

    data_frame.loc[i, 'KG'] = psi_sq

    ## Anderson-Darling test.

    sum1 = 0  # First sum
    sum2 = 0  # Second sum
    if Z[-1] == 1:
        Z[-1] -= smallest_number  # this is to avoid 0 in ln(1 - Z[-1])
    for j in range(tot_n-1):
        if Z[j + 1] == 0:
            Z[j + 1] += smallest_number  # this is to avoid 0 in ln(Z[j + 1])
        if Z[j] == 0:
            Z[j] += smallest_number  # this is to avoid 0 in ln(Z[j])
        sum1 += (G_n[j] ** 2) * (-ln(1 - Z[j + 1]) + ln(Z[j + 1]) + ln(1 - Z[j]) - ln(Z[j]))
        sum2 += G_n[j] * (-ln(1 - Z[j + 1]) + ln(1 - Z[j]))

    AC_sq = (tot_n * sum1) - (2 * tot_n * sum2) - (tot_n * ln(1 - Z[-1])) - (tot_n * ln(Z[-1])) - tot_n

    data_frame.loc[i, 'AD'] = AC_sq
data_frame = data_frame.sort_values(by='AIC', ignore_index=True)

# calculate AIC delta values (see Burnham and Anderson 2004)

for i, AIC_val in enumerate(data_frame['AIC']):
    d_i = AIC_val - data_frame['AIC'][0]

    data_frame.loc[i, 'delta_i'] = d_i

# calculate Akaike weights (see Burnham and Anderson 2004)

total = exp(-data_frame['delta_i']/2).sum()

for d, delta_i in enumerate(data_frame['delta_i']):
    w_i = np.round(exp(-delta_i/2)/total, 10)

    data_frame.loc[d, 'w_i'] = w_i


data_frame['AIC rank'] = ss.rankdata(data_frame['AIC'], nan_policy='omit')
data_frame['KS rank'] = ss.rankdata(data_frame['KS'], nan_policy='omit')
data_frame['KG rank'] = ss.rankdata(data_frame['KG'], nan_policy='omit')
data_frame['AD rank'] = ss.rankdata(data_frame['AD'], nan_policy='omit')
data_frame['Mean rank'] = data_frame.iloc[:, 7:].mean(axis=1)
data_frame = data_frame.sort_values(by='AIC', ignore_index=True)
print(data_frame)
data_frame.to_csv('analysis_output.csv')
data_frame.to_clipboard(excel=True)
np.savetxt('samples.csv', samples, delimiter=',')
