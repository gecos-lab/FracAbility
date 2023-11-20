from scipy.stats import norm, lognorm
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def lognorm_parameters(target_mean, target_std):
    """
    Get the parameters of the underlying normal distribution for mean and std of the lognorm
    :param target_mean: Target lognorm mean
    :param target_std: Target lognorm std
    """

    var_normal = np.log((target_std ** 2 / (target_mean ** 2)) + 1)

    m_normal = np.log(target_mean) - var_normal / 2

    return m_normal, np.sqrt(var_normal)


mu_n, s_n = lognorm_parameters(10, 7)

distr1 = norm(loc=0, scale=1)
distr2 = lognorm(loc=0, s=s_n, scale=np.exp(mu_n))
distr3 = lognorm(loc=5, s=s_n, scale=np.exp(mu_n))


test_data1 = distr1.rvs(size=1000)
test_data2 = distr2.rvs(size=1000)
test_data3 = distr3.rvs(size=1000)

range1 = np.linspace(min(test_data1), max(test_data1))
range2 = np.linspace(min(test_data2), max(test_data2))
range3 = np.linspace(min(test_data3), max(test_data3))

fit1 = norm.fit(test_data1)
fit2 = lognorm.fit(test_data2, floc=0)
fit3 = lognorm.fit(test_data3, floc=0)

print(fit1)
print(fit2)
print(fit3)

pdf1 = norm.pdf(range1, *fit1)
pdf2 = lognorm.pdf(range2, *fit2)
pdf3 = lognorm.pdf(range3, *fit3)

# sns.histplot(test_data1, stat='density')
sns.histplot(test_data2, stat='density')
sns.histplot(test_data3, stat='density')
# sns.lineplot(x=range1, y=pdf1)
sns.lineplot(x=range2, y=pdf2)
sns.lineplot(x=range3, y=pdf3)

plt.show()