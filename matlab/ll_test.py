import scipy.stats as ss
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as s
import reliability.Fitters
import ast

s.set_theme()

in_data = pd.read_csv('length_dist.csv')

complete = in_data.loc[in_data['U-nodes'] == 0, 'length'].values
censored = in_data.loc[in_data['U-nodes'] == 1, 'length'].values

# reliability.Fitters.Fit_Everything(failures=complete, right_censored=censored,
#                                    show_probability_plot=False,
#                                    show_PP_plot=False,
#                                    show_histogram_plot=False,
#                                    show_best_distribution_probability_plot=False
#                                    )


# s.histplot(in_data['length'].values, stat='density')
# plt.show()


data = ss.CensoredData(uncensored=complete, right=censored)

print(data)
print(data.__len__())
#
# ecdf = ss.ecdf(data).cdf
# ecdf_nc = ss.ecdf(in_data['length'].values).cdf
#
# fitt_list = ['lognorm',
#              'norm',
#              'expon',
#              'burr12',
#              'gamma',
#              'logistic']
# # data = fitter.lengths
# fig1 = plt.figure(num='CDF plots', figsize=(13, 7))
# fig2 = plt.figure(num='Histograms', figsize=(13, 7))
#
# results_temp = {'name': [], 'AICc': [], 'BIC': [], 'LL': [], 'distr': [], 'params': list}
#
# results_df = pd.DataFrame.from_dict(results_temp)
#
# for i, fitter_name in enumerate(fitt_list):
#
#     distr = getattr(ss, fitter_name)
#
#     if fitter_name == 'norm' or fitter_name == 'logistic':
#         params = distr.fit(data)
#     else:
#         params = distr.fit(data, floc=0)
#
#     logf = distr.logpdf(complete, *params)
#     logR = distr.logsf(censored, *params)
#
#     LL_f = logf.sum()
#     LL_rc = logR.sum()
#
#     LL = -(LL_f+LL_rc)
#
#     LL2 = 2*LL
#     loglik = LL2*-0.5
#
#     k = len(params)
#     n = len(complete)+len(censored)
#
#     AICc = 2*k + LL2 + (2 * k**2 + 2*k)/(n - k - 1)
#     BIC = np.log(n)*k + LL2
#
#     # print(f'================ {fitter_name} ================')
#     # print(f'LogLikelihood: {loglik}')
#     # print(f'AICc: {AICc}')
#     # print(f'BIC: {BIC}')
#     results_df.loc[i, 'name'] = fitter_name
#     results_df.loc[i, 'AICc'] = AICc
#     results_df.loc[i, 'BIC'] = BIC
#     results_df.loc[i, 'LL'] = loglik
#     results_df.loc[i, 'distr'] = distr
#     results_df.loc[i, 'params'] = str(params)
#
#
# sorted = results_df.sort_values('AICc',ignore_index=True)
#
# for i in sorted.index:
#
#     distr = sorted.loc[i, 'distr']
#     params = ast.literal_eval(sorted.loc[i, 'params'])
#     fitter_name = sorted.loc[i, 'name']
#     aicc = sorted.loc[i,'AICc']
#
#     cdf = distr.cdf(ecdf.quantiles, *params)
#     pdf = distr.pdf(ecdf.quantiles, *params)
#
#     plt.figure(num='CDF plots', sharex=True, sharey=True)
#     plt.tight_layout()
#     plt.subplot(2, 3, i+1)
#     # if i//3 < 1:
#     #     plt.tick_params(labelbottom=False)
#     # if i%3 > 0:
#     #     plt.tick_params(labelleft=False)
#     plt.title(f'{fitter_name}   AICc: {np.round(aicc,3)}')
#     plt.plot(ecdf.quantiles, ecdf.probabilities, 'b-', label='Empirical CDF')
#     plt.plot(ecdf.quantiles, cdf, 'r-', label=f'{fitter_name} CDF')
#     plt.legend()
#
#     plt.figure('Histograms')
#     plt.subplot(2, 3, i+1)
#     plt.title(f'{fitter_name}   AICc: {np.round(aicc, 3)}')
#     s.histplot(in_data['length'].values, stat='density', bins=50)
#     s.lineplot(x=ecdf.quantiles, y=pdf, label=f'{fitter_name} PDF', color='r')
#     plt.legend()
#
#
# plt.show()


