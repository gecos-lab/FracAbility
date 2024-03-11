import scipy.stats as ss
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

l = 1
x = np.linspace(0,1, num=100000)
number_of_samples = 5000
samples = np.random.exponential(l, number_of_samples)
samples.sort()


# sns.histplot(samples, bins=50, stat='density')

fdr = 1-np.exp(-l*samples)

sns.histplot(fdr, bins=50, stat='density')
plt.show()

ecdf = ss.ecdf(fdr).cdf
plt.plot(fdr, ecdf.probabilities)
plt.plot(fdr, ss.uniform.cdf(fdr))

plt.show()

# x = np.linspace(-1.0, 1.5, num=10000)
# # mean and standard deviation
# mu = 0
# sigma = 1
#
# # sample the distribution
# number_of_samples = 5000
# samples = np.random.normal(mu, sigma, number_of_samples)
# samples.sort()
#
# sample_mean = np.mean(samples)
# sample_std = np.std(samples)
#
# true_distribution = ss.norm.pdf(x, mu, sigma)
# uniform_distribution = ss.uniform.pdf(x)
#
# plt.plot(samples, ss.norm.cdf(samples))
# plt.plot(x, ss.uniform.cdf(x))
# plt.show()
#
# cdf = ss.norm.cdf(samples)
#
# sns.histplot(cdf, bins=50, stat='density')
# plt.plot(x, uniform_distribution)
# plt.show()


