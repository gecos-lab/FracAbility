import pandas as pd
import scipy.stats as ss
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme()

data = pd.read_csv('data.csv', index_col=0)
complete_data = data['length'].values

print(complete_data.mean())
print(complete_data.var())


uncensored_data = data.loc[data['censored'] == 0, 'length'].values
censored_data = data.loc[data['censored'] == 1, 'length'].values

data_set = ss.CensoredData(uncensored=uncensored_data, right=censored_data)

# ================ fitting with censoring and no floc ================

dist = ss.burr12

fit_params = dist.fit(data_set)

fitted_dist = ss.burr12(*fit_params)


print(f'censoring, no floc: {fitted_dist.stats()}')

fig = plt.figure()

ecdf = ss.ecdf(data_set).cdf
esf = ss.ecdf(data_set).sf

x_vals = ecdf.quantiles

plt.subplot(2, 2, 1)
sns.lineplot(x=complete_data, y=fitted_dist.pdf(complete_data), color='r', label='Distribution PDF')
sns.histplot(complete_data, stat='density', bins=50)

plt.subplot(2, 2, 2)
sns.lineplot(x=x_vals, y=fitted_dist.cdf(x_vals), color='r', label='Distribution CDF')
sns.lineplot(x=ecdf.quantiles, y=ecdf.probabilities, color='b', label='Empirical CDF')
plt.subplot(2, 2, 3)
sns.lineplot(x=x_vals, y=fitted_dist.sf(x_vals), color='r', label='Distribution SF')
sns.lineplot(x=esf.quantiles, y=esf.probabilities, color='b', label='Empirical SF')
plt.show()

# ================ fitting with censoring and floc = 0 ================


fit_params = dist.fit(data_set, floc=0)
print(fit_params)

fitted_dist = ss.burr12(*fit_params)

print(f'censoring, floc = 0: {fitted_dist.stats()}')


fig2 = plt.figure()

ecdf = ss.ecdf(data_set).cdf
esf = ss.ecdf(data_set).sf

x_vals = ecdf.quantiles

plt.subplot(2, 2, 1)
sns.lineplot(x=complete_data, y=fitted_dist.pdf(complete_data), color='r', label='Distribution PDF')
sns.histplot(complete_data, stat='density', bins=50)

plt.subplot(2, 2, 2)
sns.lineplot(x=x_vals, y=fitted_dist.cdf(x_vals), color='r', label='Distribution CDF')
sns.lineplot(x=ecdf.quantiles, y=ecdf.probabilities, color='b', label='Empirical CDF')
plt.subplot(2, 2, 3)
sns.lineplot(x=x_vals, y=fitted_dist.sf(x_vals), color='r', label='Distribution SF')
sns.lineplot(x=esf.quantiles, y=esf.probabilities, color='b', label='Empirical SF')
plt.show()

# ================ fitting with no censoring and no floc ================


dist = ss.burr12

fit_params = dist.fit(complete_data, method='mm')

fitted_dist = ss.burr12(*fit_params)

print(f'no censoring, no floc: {fitted_dist.stats()}')

fig3 = plt.figure()

ecdf = ss.ecdf(complete_data).cdf
esf = ss.ecdf(complete_data).sf

x_vals = ecdf.quantiles

plt.subplot(2, 2, 1)
sns.lineplot(x=complete_data, y=fitted_dist.pdf(complete_data), color='r', label='Distribution PDF')
sns.histplot(complete_data, stat='density', bins=50)

plt.subplot(2, 2, 2)
sns.lineplot(x=x_vals, y=fitted_dist.cdf(x_vals), color='r', label='Distribution CDF')
sns.lineplot(x=ecdf.quantiles, y=ecdf.probabilities, color='b', label='Empirical CDF')
plt.subplot(2, 2, 3)
sns.lineplot(x=x_vals, y=fitted_dist.sf(x_vals), color='r', label='Distribution SF')
sns.lineplot(x=esf.quantiles, y=esf.probabilities, color='b', label='Empirical SF')
plt.show()

# ================ fitting with no censoring and floc = 0 ================

dist = ss.burr12

fit_params = dist.fit(complete_data, floc = 0, method='mm')

fitted_dist = ss.burr12(*fit_params)

print(f'no censoring, floc = 0: {fitted_dist.stats()}')

fig = plt.figure()

ecdf = ss.ecdf(complete_data).cdf
esf = ss.ecdf(complete_data).sf

x_vals = ecdf.quantiles

plt.subplot(2, 2, 1)
sns.lineplot(x=complete_data, y=fitted_dist.pdf(complete_data), color='r', label='Distribution PDF')
sns.histplot(complete_data, stat='density', bins=50)

plt.subplot(2, 2, 2)
sns.lineplot(x=x_vals, y=fitted_dist.cdf(x_vals), color='r', label='Distribution CDF')
sns.lineplot(x=ecdf.quantiles, y=ecdf.probabilities, color='b', label='Empirical CDF')
plt.subplot(2, 2, 3)
sns.lineplot(x=x_vals, y=fitted_dist.sf(x_vals), color='r', label='Distribution SF')
sns.lineplot(x=esf.quantiles, y=esf.probabilities, color='b', label='Empirical SF')
plt.show()