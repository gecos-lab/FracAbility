from scipy.stats import norm, lognorm, uniform, CensoredData
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import Generator, PCG64
import pandas as pd
from scipy.optimize import fmin, minimize, OptimizeResult
import pyvista as pv

def lognorm_parameters(target_mean, target_std):
    """
    Get the parameters of the underlying normal distribution for mean and std of the lognorm
    :param target_mean: Target lognorm mean
    :param target_std: Target lognorm std
    """

    var_normal = np.log((target_std ** 2 / (target_mean ** 2)) + 1)

    m_normal = np.log(target_mean) - var_normal / 2

    return m_normal, np.sqrt(var_normal)


def log_likelihood(censored_dataset: CensoredData, distr) -> float:
    """
    Property that returns the log likelihood of the distribution. The likelihood is calculated by adding
    the cumulative sum of the log pdf and log sf of the fitted distribution.
    :return:
    """
    log_f = distr.logpdf(censored_dataset.__dict__['_uncensored'])
    log_r = distr.logsf(censored_dataset.__dict__['_right'])

    LL_f = log_f.sum()
    LL_rc = log_r.sum()

    return LL_f + LL_rc

seed = 12345
mu_n, s_n = lognorm_parameters(10, 4)

numpy_randomGen = Generator(PCG64(seed))

distr2 = lognorm(loc=0, s=s_n, scale=np.exp(mu_n))

test_data2 = distr2.rvs(size=1000)

censoring_list = uniform.rvs(0, max(test_data2)*10, size=1000)  # Values where we censor the data

dataset = pd.DataFrame({'lengths': test_data2, 'modified': test_data2, 'censored': np.zeros_like(test_data2)})
indexes = np.where(dataset['lengths'] >= censoring_list)
dataset.loc[dataset.index[indexes], 'censored'] = 1  # Flag the values > than the censoring value
dataset.loc[dataset.index[indexes], 'modified'] = censoring_list[indexes]  # Set the flagged value equal to the censoring value

censored = dataset.loc[dataset['censored'] == 1, 'modified']  # Get censored values
uncensored = dataset.loc[dataset['censored'] == 0, 'modified']  # Get uncensored values

ss_dataset = CensoredData(uncensored=uncensored, right=censored)
print(ss_dataset)
fit2 = lognorm.fit(ss_dataset, floc=0)

a, b, c = fit2
a_res = 100
c_res = 100

a_list = np.linspace(0, a, a_res)
c_list = np.linspace(0, c, c_res)
A, C = np.meshgrid(a_list, c_list)
# print(a_list, c_list)

ll_vals = np.empty(shape=(a_res, c_res))

for a_ind, a_val in enumerate(a_list):
    for c_ind, c_val in enumerate(c_list):
        print(f'{a_ind}: {c_ind}', end='\r')
        args = (a_val, b, c_val)
        ll = log_likelihood(ss_dataset, lognorm.freeze(*args))
        # if ~np.isnan(ll):
        ll_vals[a_ind, c_ind] = log_likelihood(ss_dataset, lognorm.freeze(*args))

min_val = np.min(ll_vals[~np.isnan(ll_vals)])
# print(min_val)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(np.log(A), np.log(C), ll_vals.transpose()/min_val, cmap="coolwarm", linewidth=1, antialiased=True, alpha=0.7, zorder=0)
ax.set_xlabel(r'a')
ax.set_ylabel(r'c')
ax.set_zlabel('Log-likelihood')
# ax.scatter([alpha_fit],[beta_fit],[LL_max],color='k',zorder=1)
# text_string = str(r'$\alpha=$'+str(round(alpha_fit,2))+'\n'+r'$\beta=$'+str(round(beta_fit,2))+'\nLL='+str(round(LL_max,2)))
# ax.text(x=alpha_fit,y=beta_fit,z=LL_max+0.1,s=text_string)
# ax.computed_zorder = False
# plt.title(r'Log-likelihood over a range of $\alpha$ and $\beta$ values')
plt.show()
# test = pv.StructuredGrid()
# test.points =

# # fit3 = norm.fit
# # fit3 = lognorm.fit(test_data2, floc=0)
#
# # print(fit2)
# # print(fit3)
# #
# args = lognorm._fitstart(ss_dataset)
# # print(args)
# #
# #
#
# # p = pv.Plotter()
#
# points = np.array([])
#
# def callback(intermediate_result: OptimizeResult):
#     global points
#     x, y = intermediate_result['x']
#     z = intermediate_result['fun']
#     points = np.append(points, np.array([x, y, z]))
#
#
#
# def f(x):
#     return x**2
#
# x0, func, restore, args = lognorm._reduce_func(args=args, kwds={'floc': 0, 'method': 'mle'}, data=ss_dataset)
#
# # vals = fmin(func, x0, args=(ss_dataset, ), callback=callback)
# #
# test = minimize(func, x0, args=(ss_dataset, ), callback=callback, method='Nelder-Mead')
#
# points = points.reshape(-1, 3)
# print(test)
# print(points)
# plt.plot(points[0], points[2])
# plt.show()
# # points_pv = pv.PolyData(points)
# # points_pv.plot()
#
# # print(vals)
# # print(test['x'])