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


data = pd.read_csv('Fractures_Spacing_pontrelli.csv', index_col=0)  # Read the data

data = data.sort_values(by='length')  # sort the data by length

lengths = data['length'].values  # Length value

lengths = lengths[lengths != np.nan]


sns.histplot(lengths)
plt.xlabel('Length [m]')
plt.show()
censored_value = data['censored'].values  # Censoring values: 0 is complete, 1 is censored
delta = 1-censored_value  # In the formulas delta = 1 means complete while 0 means censored.



tot_n = len(lengths)

censored = data.loc[censored_value == 1, 'length']  # Extract only the censored values
uncensored = data.loc[censored_value == 0, 'length']  # Extract only the complete values


data_cens = ss.CensoredData(uncensored, right=censored)  # Create the scipy CensoredData instance

names = ['lognorm', 'expon', 'weibull_min', 'gamma', 'logistic', 'norm']  # list of names of scipy distribution to test
# names = ['lognorm']
data_frame = pd.DataFrame(columns=['dist_name',
                                   'AIC', 'delta_i', 'w_i', 'weight_ratios',
                                   'KS', 'KG', 'AD',
                                   'AIC rank', 'KS rank', 'KG rank', 'AD rank'], dtype=float)  # Create empty final dataframe


for i, name in enumerate(names):  # for each scipy distribution do:

    data_frame.loc[i, 'dist_name'] = name

    dist = getattr(ss, name)
    if name == 'norm' or name == 'logistic':  # for normal and logistic floc controls mu, so it must not be set to 0
        params = dist.fit(data_cens)
    else:
        params = dist.fit(data_cens, floc=0)

    print(params)
    fitted_dist = dist.freeze(*params)

    print(len(uncensored))
    # Akaike 1974

    max_like = fitted_dist.logpdf(uncensored).sum()+fitted_dist.logsf(censored).sum()  # The maximum likelihood SHOULD be the sum of the total sum of logpdf(uncensored) and logsf(censored) of the fitted dist (that is estimated using MLE)
    print(fitted_dist.logpdf(uncensored).sum())
    if name == 'norm' or name == 'logistic':
        k = len(fitted_dist.args)
    else:
        k = len(fitted_dist.args) - 1 # because floc is fixed to 0, it is not considered in the maximum likelyhood and so the number of optimized arguments of the distribution are - 1

    AIC = (-2*max_like)+(2*k)

    data_frame.loc[i, 'AIC'] = AIC

    # Kim 2019

    Z = fitted_dist.cdf(lengths)
    G_n = KM(Z, Z, delta)
    plt.step(Z, G_n, label=f'G_n {name}')  # plot the Kaplan-Meier curves with steps.

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

    for j in range(tot_n-1):
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

data_frame['weight_ratios'] = data_frame['w_i'][0]/data_frame['w_i']

data_frame['AIC rank'] = ss.rankdata(data_frame['AIC'], nan_policy='omit')
data_frame['KS rank'] = ss.rankdata(data_frame['KS'], nan_policy='omit')
data_frame['KG rank'] = ss.rankdata(data_frame['KG'], nan_policy='omit')
data_frame['AD rank'] = ss.rankdata(data_frame['AD'], nan_policy='omit')
print(data_frame)
data_frame.to_csv('analysis_output.csv')

# Plot

uniform_list = np.linspace(0, 1, 100)
cdf_uniform = ss.uniform.cdf(uniform_list)
plt.plot(uniform_list, cdf_uniform, 'k--', label='U(0,1) CDF')

plt.title('Uniform comparison')
plt.legend()
plt.show()


plt.axis('off')
plt.table(cellText=data_frame.values[:, 8:],
          rowLabels=data_frame['dist_name'],
          colLabels=data_frame.columns[8:],
          loc='center'
)
plt.show()

