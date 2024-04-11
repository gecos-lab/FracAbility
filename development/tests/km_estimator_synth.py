import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import pandas as pd
import seaborn as sns


x = np.linspace(0, 1, num=1000)
number_of_samples = 1000
samples = np.random.standard_normal(number_of_samples)
samples.sort()

sns.histplot(samples)
plt.title(f'Frequency of {number_of_samples} random samples drawn from a standard normal distribution')
plt.show()

dist1 = ss.norm.freeze(*ss.norm.fit(samples))
dist2 = ss.expon.freeze(*ss.expon.fit(samples))

sns.lineplot(x=samples, y=dist1.pdf(samples))
plt.show()
sns.lineplot(x=samples, y=dist2.pdf(samples))
plt.show()

cdf_1 = dist1.cdf(samples)
cdf_2 = dist2.cdf(samples)
ecdf1 = ss.ecdf(cdf_1).cdf
ecdf2 = ss.ecdf(cdf_2).cdf

sns.histplot(cdf_1, label='Normal fit')
sns.histplot(cdf_2, label='Exponential fit')
plt.title('Frequency histogram of the CDF for the fitted distributions ')
plt.legend()
plt.show()

sns.lineplot(x=ecdf1.quantiles, y=ecdf1.probabilities, label='Normal fit')
sns.lineplot(x=ecdf2.quantiles, y=ecdf2.probabilities, label='Exponential fit')
plt.title('Empirical cumulative of the CDF for the fitted distributions ')
plt.show()