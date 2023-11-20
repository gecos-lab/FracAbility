import scipy.stats as ss
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as s

s.set_theme()

in_data = pd.read_csv('length_dist.csv')

complete = in_data.loc[in_data['U-nodes'] == 0, 'length'].values
censored = in_data.loc[in_data['U-nodes'] == 1, 'length'].values

# s.histplot(in_data['length'].values, stat='density')
# plt.show()


data = ss.CensoredData(uncensored=complete, right=censored)

ecdf = ss.ecdf(data).cdf
ecdf_nc = ss.ecdf(in_data['length'].values).cdf

fitt_list = ['lognorm',
             'norm',
             'expon',
             'burr12',
             'gamma',
             'logistic']
# data = fitter.lengths
fig1 = plt.figure(num='CDF plots', figsize=(13, 7))
fig2 = plt.figure(num='Histograms', figsize=(13, 7))

for i, fitter_name in enumerate(fitt_list):

    distr = getattr(ss, fitter_name)

    if fitter_name == 'norm' or fitter_name == 'logistic':
        params = distr.fit(data)
    else:
        params = distr.fit(data, floc=0)

    cdf = distr.cdf(ecdf.quantiles, *params)
    pdf = distr.pdf(ecdf.quantiles, *params)

    plt.figure('CDF plots')
    plt.subplot(2, 3, i+1)
    plt.title(fitter_name)
    plt.plot(ecdf_nc.quantiles, ecdf_nc.probabilities, 'b-',label='Empirical CDF')
    plt.plot(ecdf.quantiles, cdf, 'r-', label=f'{fitter_name} CDF')
    plt.legend()

    plt.figure('Histograms')
    plt.subplot(2, 3, i+1)
    plt.title(fitter_name)
    s.histplot(in_data['length'].values, stat='density',bins=50)
    s.lineplot(x=ecdf.quantiles, y=pdf, label=f'{fitter_name} PDF',color='r')
    plt.legend()

    test = ss.kstest(ecdf.probabilities, cdf, method='asymp')
    print(f'{fitter_name}: \n{params}\n{test}')

plt.show()


