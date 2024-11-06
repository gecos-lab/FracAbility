import matplotlib.pyplot as plt
import numpy as np
from numpy import exp
from numpy import log as ln
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


# data = pd.read_csv('data/Pontrelli/output/csv/Fractures_1.csv', index_col=0)
# data = pd.read_csv('data/Salza/output/csv/Fractures_1.csv', index_col=0, sep=';')
data = pd.read_csv('data/Salza/output/csv/Fractures_2.csv', index_col=0, sep=';')

# data = pd.read_csv('data/Spacing_Salza_S1/output/csv/Fractures_1.csv', index_col=0)  # Read the data
# data = pd.read_csv('data/Spacing_Salza_S2/output/csv/Fractures_1.csv', index_col=0)  # Read the data

data = data.sort_values(by='length')  # sort the data by length

lengths = data['length'].values  # Length value

lengths = lengths[lengths != np.nan]

censored_value = data['censored'].values  # Censoring values: 0 is complete, 1 is censored
delta = 1-censored_value  # In the formulas delta = 1 means complete while 0 means censored.

tot_n = len(lengths)

censored = data.loc[censored_value == 1, 'length'].values  # Extract only the censored values
uncensored = data.loc[censored_value == 0, 'length'].values  # Extract only the complete values

sns.histplot(lengths, label='Data', stat='density' )
sns.histplot(censored, label='Censored', stat='density')
plt.show()
censoring_percentage = 100*len(censored)/tot_n

data_cens = ss.CensoredData(uncensored, right=censored)  # Create the scipy CensoredData instance

name = 'weibull_min'
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

fig = plt.figure(num=f'ECDF comparison', figsize=(13, 7))

ecdf_ignore = KM(lengths, lengths, None)
ecdf_remove = KM(uncensored, uncensored, None)
ecdf_surv = KM(lengths, lengths, delta)


plt.plot(lengths, ecdf_ignore, label='ECDF ignore', drawstyle='steps')
plt.plot(uncensored, ecdf_remove, label='ECDF remove', drawstyle='steps')
plt.plot(lengths, ecdf_surv, label='ECDF survival', drawstyle='steps')
plt.annotate(f'Censoring percentage: {censoring_percentage :.2f}%', (0.75, 0.14), va='top',
             ha='left', fontsize='large', xycoords='figure fraction')

plt.title('ECDF estimation comparison')
plt.ylabel('Density')
plt.xlabel('Length [m]')
setFigLinesBW(fig)
plt.legend()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()


fig = plt.figure(num=f'Uniform ECDF comparison', figsize=(13, 7))

gn_ecdf_ignore = KM(ecdf_ignore, ecdf_ignore, delta)
gn_ecdf_remove = KM(ecdf_remove, ecdf_remove, delta)
gn_ecdf_surv = KM(ecdf_surv, ecdf_surv, delta)


plt.plot(ecdf_ignore, gn_ecdf_ignore, label='ECDF ignore', drawstyle='steps')
plt.plot(ecdf_remove, gn_ecdf_remove, label='ECDF remove', drawstyle='steps')
plt.plot(ecdf_surv, gn_ecdf_surv, label='ECDF survival', drawstyle='steps')
plt.annotate(f'Censoring percentage: {censoring_percentage :.2f}%', (0.75, 0.14), va='top',
             ha='left', fontsize='large', xycoords='figure fraction')

plt.title('Uniform ECDF estimation comparison')
setFigLinesBW(fig)
plt.plot([0, 1], [0, 1], label='U (0,1)', color='red')
plt.legend()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()


fig = plt.figure(num=f'CDF comparison', figsize=(13, 7))
plt.annotate(f'Censoring percentage: {censoring_percentage :.2f}%', (0.75, 0.14), va='top',
             ha='left', fontsize='large', xycoords='figure fraction')

Z_ignore = ignore_censoring.cdf(lengths)
Z_remove = remove_censored.cdf(lengths)
Z_survival = survival.cdf(lengths)

plt.plot(lengths, Z_ignore, label='CDF ignore', drawstyle='steps')
plt.plot(lengths, Z_remove, label='CDF remove', drawstyle='steps')
plt.plot(lengths, Z_survival, label='CDF survival', drawstyle='steps')

plt.title('CDF estimation comparison')
plt.xlabel('Length [m]')
plt.ylabel('Density')
setFigLinesBW(fig)
plt.plot(lengths, ecdf_surv, label='ECDF survival',color='red', drawstyle='steps')
plt.legend()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()


fig = plt.figure(num=f'PDF comparison', figsize=(13, 7))
plt.annotate(f'Censoring percentage: {censoring_percentage :.2f}%', (0.75, 0.14), va='top',
             ha='left', fontsize='large', xycoords='figure fraction')

pdf_ignore = ignore_censoring.pdf(lengths)
pdf_remove = remove_censored.pdf(lengths)
pdf_survival = survival.pdf(lengths)

plt.plot(lengths, pdf_ignore, label='CDF ignore', drawstyle='steps')
plt.plot(lengths, pdf_remove, label='CDF remove', drawstyle='steps')
plt.plot(lengths, pdf_survival, label='CDF survival', drawstyle='steps')

plt.title('PDF estimation comparison')
plt.xlabel('Length [m]')
plt.ylabel('Density')
setFigLinesBW(fig)
sns.histplot(lengths, label='Data', stat='density')
plt.legend()
figManager = plt.get_current_fig_manager()
figManager.window.showMaximized()


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


# loc_list = ['norm', 'logistic']

#data_frame = pd.DataFrame(columns=['dist_name',
                                   # 'AIC', 'delta_i', 'w_i',
                                   # 'KS', 'KG', 'AD',
                                   # 'AIC rank', 'KS rank', 'KG rank', 'AD rank','Mean rank'], dtype=float)  # Create empty final dataframe


# data_frame['dist_name'] = data_frame['dist_name'].astype(str)
#     # Akaike 1974
#
#     name = dict_value
#     data_frame.loc[i, 'dist_name'] = name
#     fitted_dist = dist_dict[name]
#
#     if 'ignore' in name:
#         max_like = fitted_dist.logpdf(lengths).sum()  # The maximum likelihood SHOULD be the sum of the total sum of logpdf(uncensored) and logsf(censored) of the fitted dist (that is estimated using MLE)
#     elif 'remove' in name:
#         max_like = fitted_dist.logpdf(uncensored).sum()
#     else:
#         max_like = fitted_dist.logpdf(uncensored).sum() + fitted_dist.logsf(censored).sum()
#
#     if name in loc_list:
#         k = len(fitted_dist.args)
#     else:
#         k = len(fitted_dist.args) - 1 # because floc is fixed to 0, it is not considered in the maximum likelihood and so the number of optimized arguments of the distribution are - 1
#
#     AIC = (-2*max_like)+(2*k)
#
#     data_frame.loc[i, 'AIC'] = AIC
#
#     # Kim 2019
#
#     Z = fitted_dist.cdf(lengths)
#     G_n = KM(Z, Z, delta)
#     plt.plot(lengths, Z, label=f'{name}', drawstyle='steps')  # plot the Kaplan-Meier curves with steps.
#
#     ## Kolmogorov-Smirnov test
#
#     complete_list_index = np.where(delta == 1)[0]
#
#     diff_plus_list = []
#     diff_minus_list = []
#
#     for j in complete_list_index:
#         diff_plus = G_n[j]-Z[j]  # Calculate the positive difference at index j (DC+)
#
#         if j+1 > tot_n-1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
#             Z_j1 = 1
#         else:
#             Z_j1 = Z[j+1]
#
#         diff_minus = Z_j1-G_n[j]  # Calculate the negative difference at index j (DC-)
#         diff_plus_list.append(diff_plus)
#         diff_minus_list.append(diff_minus)
#
#     DCn_pos = max(diff_plus_list)
#     DCn_neg = max(diff_minus_list)
#
#     DCn = max(DCn_pos, DCn_neg)
#
#     data_frame.loc[i, 'KS'] = DCn
#
#     ## Koziol and Green test
#
#     kg_sum = 0
#
#     for j in range(tot_n):
#
#         if j+1 > tot_n-1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
#             Z_j1 = 1
#         else:
#             Z_j1 = Z[j+1]
#         kg_sum += G_n[j]*(Z_j1-Z[j])*(G_n[j]-(Z_j1+Z[j]))
#
#     psi_sq = (tot_n*kg_sum)+tot_n/3
#
#     data_frame.loc[i, 'KG'] = psi_sq
#
#     ## Anderson-Darling test.
#
#     sum1 = 0  # First sum
#     sum2 = 0  # Second sum
#     if Z[-1] == 1:
#         Z[-1] -= 10**-10  # this is to avoid 0 in ln(1 - Z[-1]) and similar
#     for j in range(tot_n-1):
#
#         sum1 += (G_n[j] ** 2) * (-ln(1 - Z[j + 1]) + ln(Z[j + 1]) + ln(1 - Z[j]) - ln(Z[j]))
#         sum2 += G_n[j] * (-ln(1 - Z[j + 1]) + ln(1 - Z[j]))
#
#     AC_sq = (tot_n * sum1) - (2 * tot_n * sum2) - (tot_n * ln(1 - Z[-1])) - (tot_n * ln(Z[-1])) - tot_n
#
#     data_frame.loc[i, 'AD'] = AC_sq
#
# data_frame = data_frame.sort_values(by='AIC', ignore_index=True)
#
#
# # calculate AIC delta values (see Burnham and Anderson 2004)
#
# for i, AIC_val in enumerate(data_frame['AIC']):
#     d_i = AIC_val - data_frame['AIC'][0]
#
#     data_frame.loc[i, 'delta_i'] = d_i
#
# # calculate Akaike weights (see Burnham and Anderson 2004)
#
# total = exp(-data_frame['delta_i']/2).sum()
#
# for d, delta_i in enumerate(data_frame['delta_i']):
#     w_i = np.round(exp(-delta_i/2)/total, 10)
#
#     data_frame.loc[d, 'w_i'] = w_i
#
#
# data_frame['AIC rank'] = ss.rankdata(data_frame['AIC'], nan_policy='omit')
# data_frame['KS rank'] = ss.rankdata(data_frame['KS'], nan_policy='omit')
# data_frame['KG rank'] = ss.rankdata(data_frame['KG'], nan_policy='omit')
# data_frame['AD rank'] = ss.rankdata(data_frame['AD'], nan_policy='omit')
# data_frame['Mean rank'] = data_frame.iloc[:, 7:].mean(axis=1)
# # print(data_frame)
# data_frame.to_csv('analysis_output.csv')
#
# # Plot
#
# uniform_list = np.linspace(0, 1, 100)
# cdf_uniform = ss.uniform.cdf(uniform_list)
# setFigLinesBW(fig)
# # plt.plot(uniform_list, cdf_uniform, 'r', label='U(0, 1)')
# plt.text(0.75, 0, f'Censoring percentage: {censoring_percentage :.2f}%', va='top', ha='left', fontsize='large')
# plt.title('Distance to Uniform comparison')
# plt.legend()
# plt.show()
#
#
# # plt.axis('off')
# # the_table = plt.table(cellText=data_frame.round(decimals=2).values[:,1:],
# #           rowLabels=data_frame['dist_name'],
# #           colLabels=data_frame.columns[1:],
# #           loc='center')
# #
# # the_table.auto_set_font_size(False)
# # the_table.auto_set_column_width(col=list(range(len(data_frame.columns))))
# # the_table.set_fontsize(14)
# # # the_table.scale(2, 2)
# # plt.show()

