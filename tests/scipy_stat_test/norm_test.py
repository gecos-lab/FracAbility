from scipy.stats import norm
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

distr1 = norm(loc=0, scale=1)
distr2 = norm(loc=10, scale=1)
distr3 = norm(loc=5, scale=5)


test_data1 = distr1.rvs(size=1000)
test_data2 = distr2.rvs(size=1000)
test_data3 = distr3.rvs(size=1000)

range1 = np.linspace(min(test_data1), max(test_data1))
range2 = np.linspace(min(test_data2), max(test_data2))
range3 = np.linspace(min(test_data3), max(test_data3))

fit1 = norm.fit(test_data1)
fit2 = norm.fit(test_data2)
fit3 = norm.fit(test_data3)

print(fit1)
print(fit2)
print(fit3)

pdf1 = norm.pdf(range1, *fit1)
pdf2 = norm.pdf(range2, *fit2)
pdf3 = norm.pdf(range3, *fit3)

sns.histplot(test_data1, stat='density')
sns.histplot(test_data2, stat='density')
sns.histplot(test_data3, stat='density')
sns.lineplot(x=range1, y=pdf1)
sns.lineplot(x=range2, y=pdf2)
sns.lineplot(x=range3, y=pdf3)

plt.show()