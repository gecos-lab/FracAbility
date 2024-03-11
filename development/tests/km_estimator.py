import matplotlib.pyplot as plt
import numpy as np
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

    for j in j_index: # for each index in the index list
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
    # Sort Z in case it is not sorted at input
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


def ln(number):
    """
    Natural logarithm. Function created to make it more readable the formulas
    """
    return np.log(number)


data = pd.read_csv('Fractures_test.csv', index_col=0)  # Read the data

data = data.sort_values(by='length')  # sort the data by length

lengths = data['length'].values  # Length value
censored_value = data['censored'].values  # Censoring values: 0 is complete, 1 is censored
delta = 1-censored_value  # In the formulas delta = 1 means complete while 0 means censored.
tot_n = len(lengths)

censored = data.loc[censored_value == 1, 'length']  # Extract only the censored values
uncensored = data.loc[censored_value == 0, 'length']  # Extract only the complete values

data_cens = ss.CensoredData(uncensored, right=censored)  # Create the scipy CensoredData instance

# Reference uniform (0,1)


names = ['lognorm', 'expon', 'norm']  # list of names of scipy distribution to test

data_frame = pd.DataFrame(columns=['dist_name', 'KS test', 'KG test', 'AD test'])


for i, name in enumerate(names):  # for each scipy distribution do:

    dist = getattr(ss, name)
    if name == 'norm' or 'logistic':  # for normal and logistic floc controls mu
        params = dist.fit(data_cens)
    else:
        params = dist.fit(data_cens, floc=0)
    fitted_dist = dist.freeze(*params)

    Z = fitted_dist.cdf(lengths)
    G_n = KM(Z, Z, delta)
    plt.step(Z, G_n, label=f'G_n {name}',)

    # Kolmogorov-Smirnov test

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
    # print(f'KS {name}: {DCn}')

    # Koziol and Green test

    kg_sum = 0

    for j in range(tot_n):

        if j+1 > tot_n-1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
            Z_j1 = 1
        else:
            Z_j1 = Z[j+1]
        kg_sum += G_n[j]*(Z_j1-Z[j])*(G_n[j]-(Z_j1+Z[j]))

    psi_sq = (tot_n*kg_sum)+tot_n/3

    # print(f'Psi^2 {name}: {psi_sq}')

    # Anderson-Darling test.

    sum1 = 0  # First sum
    sum2 = 0  # Second sum

    for j in range(tot_n-1):
        sum1 += (G_n[j] ** 2) * (-ln(1 - Z[j + 1]) + ln(Z[j + 1]) + ln(1 - Z[j]) - ln(Z[j]))
        sum2 += G_n[j] * (-ln(1 - Z[j + 1]) + ln(1 - Z[j]))

    AC_sq = (tot_n * sum1) - (2 * tot_n * sum2) - (tot_n * ln(1 - Z[-1])) - (tot_n * ln(Z[-1])) - tot_n

    # print(f'AC^2 {name}: {AC_sq}')

    data_frame.loc[i] = [name, DCn, psi_sq, AC_sq]

print(data_frame)

uniform_list = np.linspace(0, 1, 100)
cdf_uniform = ss.uniform.cdf(uniform_list)
plt.plot(uniform_list, cdf_uniform, 'k--', label='U(0,1) CDF')

plt.title('Uniform comparison')
plt.legend()
plt.show()





# diff_pos = KM_z[complete_list_index]-ecdf_Z.probabilities[complete_list_index]
#
# DCn_pos = max(diff_pos)
#
# diff_neg = ecdf_Z.probabilities[complete_list_index]-KM_z[complete_list_index]
#
# DCn_neg = max(diff_neg)
#
# print(max(DCn_pos, DCn_neg))

# sns.lineplot(x=lengths, y=Z, label='fitted CDF')
# sns.lineplot(x=lengths, y=KM_l, label='KM CDF')
# # sns.lineplot(x=ecdf_data.quantiles, y=ecdf_data.probabilities, label='ecdf length')
# plt.plot(lengths,Z)
# plt.plot(lengths, KM_l)
# plt.xlabel('length [m]')
# plt.ylabel('Density')
#
# plt.title('CDF comparison')
# plt.legend()
# plt.show()

#
# sns.lineplot(x=z_values, y=cdf_uniform, label='U(0,1) CDF')
# sns.lineplot(x=Z, y=KM_z, label='KM CDF')
# sns.lineplot(x=ecdf_Z.quantiles, y=ecdf_Z.probabilities, label='ecdf Z')
# plt.title('Uniform comparison')
# plt.legend()
# plt.show()


# print(KM([Z[0]], Z, delta))

