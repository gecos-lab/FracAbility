import scipy.stats as ss
import pandas as pd
import numpy as np
import sys

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme()

data = pd.read_csv('data.csv', index_col=0)

tot_n = len(data)

lengths = data['length'].values


name = 'burr12'

dist = getattr(ss, name)

params = dist.fit(lengths)
fitted_dist = dist.freeze(*params)

sorted = np.sort(lengths)
np.set_printoptions(threshold=sys.maxsize)

n_samples = len(lengths)
n_bins = int(2*(n_samples**(2/5)))  # https://www.itl.nist.gov/div898/handbook//prc/section2/prc211.htm
# n_bins = 5
split_array = np.array_split(sorted, n_bins)

list_bins = []

f_th = []

for i, value in enumerate(split_array):
    if i == 0:
        min = 0
        max = np.max(value)
        p = fitted_dist.cdf(max)
    elif i == n_bins-1:
        min = np.max(list_bins[-1])
        max = np.max(value)
        p = fitted_dist.sf(min)
    else:
        min = np.max(list_bins[-1])
        max = np.max(value)
        p = fitted_dist.cdf(max) - fitted_dist.cdf(min)

    list_bins.append([min, max])
    f_th.append(n_samples*p)

ran = np.unique(np.array(list_bins).flatten())
f_obs, _ = (np.histogram(sorted, bins=ran))

print(sum(f_obs))
print(sum(f_th))

result = ss.chisquare(f_obs, f_th, ddof=len(params), axis=0)

alpha = 0.05

if result.pvalue > alpha:
    print(f'pvalue {result.pvalue} higher than alpha {alpha} -> We accept the null hypothesis: The data follows the dist')
else:
    print(f'pvalue {result.pvalue} lower than alpha {alpha} -> We reject the null hypothesis: The data does not follow the dist')


fig = plt.figure(num=f'{name} PDF plot', figsize=(13, 7))


x_vals = lengths

y_vals = fitted_dist.pdf(x_vals)

sns.lineplot(x=x_vals, y=y_vals, color='r', label=f'{name} pdf')

sns.histplot(x_vals, stat='density', bins=n_bins)


plt.xlabel('length [m]')
plt.title('PDF')
plt.grid(True)
plt.legend()
plt.show()

#
# print(list_bins)

#     f_obs.append(len(i))
#
#     # print(max)
#     #
#     # print(fitted_dist.cdf(max))
#
#     p = fitted_dist.cdf(max)-fitted_dist.cdf(min)
#     f_th.append(tot_n*p)
#
#
# print(sum(f_obs), sum(f_th))




# print(result.chisq, result.pvalue)




# n = len(data)
#
# print(n)
#
# n_bin = int(2*n**(2/5))
#
# hist, _ = np.histogram(data['length'], bins=2)
# print(hist)
#
#
#
# censored = data.loc[data['censored'] == 1, 'length']
#
# uncensored = data.loc[data['censored'] == 0, 'length']
#
# dataset = ss.CensoredData(uncensored=uncensored, right=censored)
#
# dist = ss.norm
#
# params = dist.fit(dataset)
#
# fitted_dist = ss.norm(params)
