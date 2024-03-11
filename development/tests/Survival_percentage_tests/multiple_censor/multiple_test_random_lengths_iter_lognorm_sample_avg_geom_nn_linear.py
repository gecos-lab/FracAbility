"""

Test survival analysis feasibility for multiple censored events.

1. Every event starts at the same point
2. Every event has a randomly distributed length following a lognormal distribution
3. Every event is censored at different values following a uniform distribution that shifts to the left (removing the same
amount each iteration). We end the shift only when 100% censoring is reached. The step follows a geometric succession


After each iteration we interpolate the data using nn and normal linear interpolation to confront the two.
We test the effects of the % censoring on the fitting of a known distribution by plotting the % of censored values
with the sample average. We run n iterations and mean them to get an overall trend. This should provide a better plot
that shows the effect of censoring because we exclude the effect of random sampling on the estimation of the real mean.

"""

import scipy.stats as ss
from scipy.interpolate import interp1d
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from numpy.random import Generator, PCG64
import time
sns.set_theme()


def interp_nn(resample_points, raw_x, raw_y):
    resample_data = np.zeros_like(resample_points)

    for r, res_point in enumerate(resample_points):
        distances = np.abs(res_point-raw_x)
        min_dist_index = np.where(distances == distances.min())[0]
        for idx in min_dist_index:
            resample_data[r] = raw_y[idx]

    return resample_data


def plot_survival(start_times, end_times, censoring = None, name = None):
    """
    Function used to plot a survival diagram

    :param start_times: list of start times
    :param end_times: list of end times
    """

    if censoring is not None:
        if len(censoring) == 1:
            censoring_points = np.repeat(censoring, len(start_times))
        else:
            censoring_points = censoring

        for i, (start, end, censoring) in enumerate(zip(start_times, end_times, censoring_points)):
            plt.scatter(end, i, color='r', marker='^')
            plt.scatter(start, i, color='b', marker='o')
            plt.scatter(censoring, i, color='y', marker='|', s=100)
            plt.hlines(y=i, xmin=start, xmax=end)
    else:
        for i, (start, end) in enumerate(zip(start_times, end_times)):
            plt.scatter(end, i, color='r', marker='^')
            plt.scatter(start, i, color='b', marker='o')
            plt.hlines(y=i, xmin=start, xmax=end)
    # plt.savefig(name, dpi=200)
    plt.show()


def lognorm_parameters(target_mean, target_std):
    """
    Get the parameters of the underlying normal distribution for mean and std of the lognorm
    :param target_mean: Target lognorm mean
    :param target_std: Target lognorm std
    """

    var_normal = np.log((target_std ** 2 / (target_mean ** 2)) + 1)

    m_normal = np.log(target_mean) - var_normal / 2

    return m_normal, np.sqrt(var_normal)


distr = ss.lognorm
mean = 4.94
std = 6.52
n_lines = 1000
n_iterations = 10  # Number of iterations
n_windows = 500  # number of windows used to censor the values
resample_line = np.arange(0, 100.1, 0.01)  # Values used to resample the mean values


iter_mean_everything_interpolated_list = np.empty((n_iterations, len(resample_line)))
iter_mean_nocensor_interpolated_list = np.empty((n_iterations, len(resample_line)))
iter_mean_censor_interpolated_list = np.empty((n_iterations, len(resample_line)))
iter_percentage_censoring_list = np.empty((n_iterations, n_windows))

iter_mean_everything_interpolated_list_nn = iter_mean_everything_interpolated_list.copy()
iter_mean_nocensor_interpolated_list_nn = iter_mean_nocensor_interpolated_list.copy()
iter_mean_censor_interpolated_list_nn = iter_mean_censor_interpolated_list.copy()


mu_l, std_l = lognorm_parameters(mean, std)

sim_dict = {}
for i in range(n_iterations):
    print(f'iter: {i}\n')

    percentage_censoring_list_raw = []
    percentage_censoring_list = []

    mean_everything_list_raw = []  # list of means for fitting all the data
    mean_everything_list = []  # list of means for fitting all the data

    mean_nocensor_list_raw = []  # list of means for fitting excluding censored data
    mean_nocensor_list = []  # list of means for fitting excluding censored data

    mean_censor_list_raw = []  # list of means for fitting using censoring
    mean_censor_list = []

    lengths = distr.rvs(s=std_l, scale=np.exp(mu_l), size=n_lines)

    sample_mean = np.mean(lengths)

    starts = np.zeros_like(lengths)

    ends = starts+lengths

    minimum_end = min(ends)  # Min start value
    maximum_end = max(ends)  # Max end value

    dataset = pd.DataFrame({'starts': starts, 'ends': ends, 'og': lengths,
                            'modified': lengths, 'censored': np.zeros_like(lengths)})
    n_total = len(dataset)

    censoring_list = ss.uniform.rvs(0, minimum_end,
                                    size=n_lines)  # Values where we censor the data

    censoring_list_mod = censoring_list.copy() # copy of the original values that will be multiplied

    min_censor = min(censoring_list)  # smallest censoring event
    max_censor = max(censoring_list)
    k = maximum_end/min_censor
    value_range = np.geomspace(1, k, n_windows)

    steps_list = np.arange(len(value_range))
    for counter, molt_factor in enumerate(value_range):
        # print(molt_factor)
        censoring_list_mod = censoring_list * molt_factor
        # censoring_list[censoring_list <= 0] = ends[censoring_list <= 0]/10
        indexes = np.where(dataset['ends'] >= censoring_list_mod)
        dataset.loc[dataset.index[indexes], 'censored'] = 1  # Flag the values > than the censoring value
        dataset.loc[dataset.index[indexes], 'modified'] = censoring_list_mod[indexes]  # Set the flagged value equal to the censoring value

        censored = dataset.loc[dataset['censored'] == 1, 'modified']  # Get censored values
        uncensored = dataset.loc[dataset['censored'] == 0, 'modified']  # Get uncensored values

        n_censored = len(censored)  # number of censored values
        # print(n_censored)
        # plot_survival(starts, ends, censoring_values, f"survp_{mean}_{std}.png")

        percentage_censored = 100*(n_censored/n_total)
        percentage_censoring_list_raw.append(percentage_censored)
        print(f'{counter}/{len(value_range)}: {percentage_censored}', end='\r')

        # Fit everything

        params_all = distr.fit(dataset['modified'], floc=0)
        fitted_all = distr(*params_all)
        everything_diff = fitted_all.mean()-sample_mean
        mean_everything_list_raw.append(everything_diff)

        # Fit only non censored

        if len(uncensored) == 0:
            nocensor_diff = np.nan
        else:
            params_nocens = distr.fit(uncensored, floc=0)
            fitted_nocens = distr(*params_nocens)
            nocensor_diff = fitted_nocens.mean()-sample_mean

        mean_nocensor_list_raw.append(nocensor_diff)

        # Fit with censoring

        ss_dataset = ss.CensoredData(uncensored=uncensored, right=censored)

        params_cens = distr.fit(ss_dataset, floc=0)
        fitted_cens = distr(*params_cens)

        cens_diff = fitted_cens.mean() - sample_mean
        mean_censor_list_raw.append(cens_diff)

        # Construct interpolation dataset

        if percentage_censored not in percentage_censoring_list:
            mean_everything_list.append(everything_diff)

            mean_nocensor_list.append(nocensor_diff)

            mean_censor_list.append(cens_diff)

            percentage_censoring_list.append(percentage_censored)
        else:
            index = percentage_censoring_list.index(percentage_censored)

            mean_value_everything = np.mean([mean_everything_list[index], everything_diff])
            mean_everything_list[index] = mean_value_everything

            mean_value_nocens = np.mean([mean_nocensor_list[index], nocensor_diff])
            mean_nocensor_list[index] = mean_value_nocens

            mean_value_censor = np.mean([mean_censor_list[index], cens_diff])
            mean_censor_list[index] = mean_value_censor

        dataset['modified'] = dataset['og']  # Reset the values
        dataset['censored'] = 0  # Reset the censoring flag
        # if percentage_censored < 10:
        #     break

    interpolated_values_everything = np.interp(resample_line,
                                               percentage_censoring_list[::-1],
                                               mean_everything_list[::-1])

    iter_mean_everything_interpolated_list[i, :] = interpolated_values_everything

    interpolated_values_nocensor = np.interp(resample_line,
                                             percentage_censoring_list[::-1],
                                             mean_nocensor_list[::-1])

    iter_mean_nocensor_interpolated_list[i, :] = interpolated_values_nocensor

    interpolated_values_censoring = np.interp(resample_line,
                                              percentage_censoring_list[::-1],
                                              mean_censor_list[::-1])

    iter_mean_censor_interpolated_list[i, :] = interpolated_values_censoring

    interpolated_values_everything_nn = interp_nn(resample_line,
                                                  percentage_censoring_list[::-1],
                                                  mean_everything_list[::-1])

    iter_mean_everything_interpolated_list_nn[i, :] = interpolated_values_everything_nn

    interpolated_values_nocensor_nn = interp_nn(resample_line,
                                                percentage_censoring_list[::-1],
                                                mean_nocensor_list[::-1])

    iter_mean_nocensor_interpolated_list_nn[i, :] = interpolated_values_nocensor_nn

    interpolated_values_censoring_nn = interp_nn(resample_line,
                                                 percentage_censoring_list[::-1],
                                                 mean_censor_list[::-1])

    iter_mean_censor_interpolated_list_nn[i, :] = interpolated_values_censoring_nn

    # ax.plot(percentage_censoring_list, mean_everything_list, alpha=1/n_iterations, color='r')
    # ax.plot(percentage_censoring_list, mean_nocensor_list, alpha=1/n_iterations, color='b')
    # plt.plot(percentage_censoring_list_raw, mean_censor_list_raw, 'go')
    # plt.plot(percentage_censoring_list, mean_censor_list, 'bo')
    # plt.plot(resample_line, iter_mean_censor_interpolated_list[i], 'yx')
    # plt.show()
    # print(percentage_censoring_list_raw)
    plt.plot(percentage_censoring_list_raw, 'k-o', markersize=2)
    plt.xlabel('Step (s)')
    plt.ylabel('% censored (p)')
    # plt.savefig(f'images/interp/step_p_{i}.png', dpi=200)
    # plt.show()
    plt.close()
    plt.plot(mean_censor_list_raw, 'k-o', markersize=2)
    plt.xlabel('Step (s)')
    plt.ylabel('Delta')
    # plt.savefig(f'images/interp/step_d_{i}.png', dpi=200)
    # plt.show()
    plt.close()
    plt.plot(percentage_censoring_list_raw, mean_censor_list_raw, 'go')
    plt.plot(percentage_censoring_list_raw, mean_censor_list_raw, 'b-')
    plt.xlabel('% censoring')
    plt.ylabel('Delta')
    # plt.savefig(f'images/interp/raw_{i}.png', dpi=200)
    # plt.show()
    plt.close()
    plt.plot(percentage_censoring_list_raw, mean_censor_list_raw, 'go')
    plt.plot(percentage_censoring_list, mean_censor_list, 'bo')
    plt.plot(resample_line, iter_mean_censor_interpolated_list[i], 'y-')
    plt.xlabel('% censoring')
    plt.ylabel('Delta')
    # plt.savefig(f'images/interp/interp_{i}.png', dpi=200)
    # plt.show()
    plt.close()
    print('\n')


mean_everything_curve = np.mean(iter_mean_everything_interpolated_list, axis=0)
mean_nocensor_curve = np.mean(iter_mean_nocensor_interpolated_list, axis=0)
mean_censoring_curve = np.mean(iter_mean_censor_interpolated_list, axis=0)
mean_censoring_curve_nn = np.mean(iter_mean_censor_interpolated_list_nn, axis=0)

std_percent_everything = np.std(iter_mean_everything_interpolated_list, axis=0)  # std for each censoring % step
std_percent_nocensor = np.std(iter_mean_nocensor_interpolated_list, axis=0)  # std for each censoring % step
std_percent_censor = np.std(iter_mean_censor_interpolated_list, axis=0)  # std for each censoring % step
std_percent_censor_nn = np.std(iter_mean_censor_interpolated_list_nn, axis=0)  # std for each censoring % step


# print(mean_censoring_curve)

# # print(test)
# print(sim_dict[1]['percentage_list'])
# print(sim_dict[1]['mean_cens_list'])
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, sharex=True)
#
# ax.fill_between(resample_line, mean_everything_curve-std_percent_everything,
#                 mean_everything_curve+std_percent_everything,
#                 alpha=0.5, color='r')
#
# ax.plot(resample_line, mean_everything_curve, color='r', label='Fit using everything')
#
# ax.fill_between(resample_line, mean_nocensor_curve-std_percent_nocensor,
#                 mean_nocensor_curve+std_percent_nocensor,
#                 alpha=0.5, color='b')
# ax.plot(resample_line, mean_nocensor_curve, color='b', label='Fit using only complete values')

ax1.fill_between(resample_line, mean_censoring_curve-(3*std_percent_censor),
                mean_censoring_curve+(3*std_percent_censor),
                alpha=1, color='r', label='3 sigma')

ax2.fill_between(resample_line, mean_censoring_curve_nn-(3*std_percent_censor_nn),
                mean_censoring_curve_nn+(3*std_percent_censor_nn),
                alpha=1, color='r', label='3 sigma')

ax1.fill_between(resample_line, mean_censoring_curve-(2*std_percent_censor),
                mean_censoring_curve+(2*std_percent_censor),
                alpha=1, color='g', label='2 sigma')
ax2.fill_between(resample_line, mean_censoring_curve_nn-(2*std_percent_censor_nn),
                mean_censoring_curve_nn+(2*std_percent_censor_nn),
                alpha=1, color='g', label='2 sigma')

ax1.fill_between(resample_line, mean_censoring_curve-std_percent_censor,
                mean_censoring_curve+std_percent_censor,
                alpha=1, color='y', label='1 sigma')
ax2.fill_between(resample_line, mean_censoring_curve_nn-std_percent_censor_nn,
                mean_censoring_curve_nn+std_percent_censor_nn,
                alpha=1, color='y', label='1 sigma')

ax1.plot(resample_line, mean_censoring_curve, color='k', label='Fit using survival nn')
ax2.plot(resample_line, mean_censoring_curve_nn, color='k', label='Fit using survival linear')

inspection_value = 8.9
inspection_value_idx = np.where(resample_line == inspection_value)[0][0]  # % value to get the mean estimation value

print(f'value at {resample_line[inspection_value_idx]}% fitting everything: {mean_everything_curve[inspection_value_idx]}')
print(f'value at {resample_line[inspection_value_idx]}% fitting only complete measurements: {mean_nocensor_curve[inspection_value_idx]}')
print(f'value at {resample_line[inspection_value_idx]}% fitting everything with survival: {mean_censoring_curve[inspection_value_idx]}')

ax1.set_xlabel('% censored')
ax1.set_ylabel('Estimated mean - Sample mean')
ax1.set_ylim([-(mean+std+3), mean+std+3])
ax1.set_title(f'{n_lines} data points drawn from lognormal ({mean}, {std}). {n_iterations} iterations. Linear interpolation')
ax1.legend()
ax2.legend()
ax2.set_ylim([-(mean+std+3), mean+std+3])
ax1.set_title(f'{n_lines} data points drawn from lognormal ({mean}, {std}). {n_iterations} iterations. NN interpolation')


plt.suptitle('Survival analysis estimation performance comparison')
# plt.savefig(f'images/{mean}_{std}.png', dpi=200)
plt.show()

fig, ax = plt.subplots()

ax.fill_between(resample_line, mean_censoring_curve-(3*std_percent_censor),
                mean_censoring_curve+(3*std_percent_censor),
                alpha=1, color='r', label='3 sigma')

ax.fill_between(resample_line, mean_censoring_curve_nn-(3*std_percent_censor_nn),
                mean_censoring_curve_nn+(3*std_percent_censor_nn),
                alpha=1, color='c', label='3 sigma')

ax.fill_between(resample_line, mean_censoring_curve-(2*std_percent_censor),
                mean_censoring_curve+(2*std_percent_censor),
                alpha=1, color='g', label='2 sigma')
ax.fill_between(resample_line, mean_censoring_curve_nn-(2*std_percent_censor_nn),
                mean_censoring_curve_nn+(2*std_percent_censor_nn),
                alpha=1, color='b', label='2 sigma')

ax.fill_between(resample_line, mean_censoring_curve-std_percent_censor,
                mean_censoring_curve+std_percent_censor,
                alpha=1, color='y', label='1 sigma')
ax.fill_between(resample_line, mean_censoring_curve_nn-std_percent_censor_nn,
                mean_censoring_curve_nn+std_percent_censor_nn,
                alpha=1, color='m', label='1 sigma')

ax.plot(resample_line, mean_censoring_curve, 'k--', label='Fit using survival linear')
ax.plot(resample_line, mean_censoring_curve_nn, 'k', label='Fit using survival nn')
ax.set_ylim([-(mean+std+3), mean+std+3])
plt.show()