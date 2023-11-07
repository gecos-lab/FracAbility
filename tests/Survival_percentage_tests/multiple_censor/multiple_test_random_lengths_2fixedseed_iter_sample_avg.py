"""

Test survival analysis feasibility for multiple censored events.

1. Every event starts at the same point
2. Every event has a randomly distributed length following a normal distribution
3. Every event is censored at different values following a uniform distribution that shifts to right (adding the same
amount each iteration). The seed of the uniform is fixed and so the censored events are always the same each time

We test the effects of the % censoring on the fitting of a known distribution by plotting the % of censored values
with the sample average. We run n iterations and mean them to get an overall trend. This should provide a better plot
that shows the effect of censoring because we exclude the effect of random sampling on the estimation of the real mean.

"""

import scipy.stats as ss
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from numpy.random import Generator, PCG64

sns.set_theme()


def plot_survival(start_times, end_times, censoring = None):
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


distr = ss.norm
mean = 10
std = 4
n_lines = 1000
n_iterations = 100  # Number of iterations
seed = 12345
n_windows = 50  # number of windows used to censor the values


numpy_randomGen = Generator(PCG64(seed))


iter_mean_everything_list = np.empty((n_iterations, n_windows))
iter_mean_nocensor_list = np.empty((n_iterations, n_windows))
iter_mean_censor_list = np.empty((n_iterations, n_windows))
iter_percentage_censoring_list = np.empty((n_iterations, n_windows))

mu_l, std_l = lognorm_parameters(mean, std)

for i in range(n_iterations):
    print(f'iter: {i}', end='\r')

    percentage_censoring_list = []
    mean_everything_list = []  # list of means for fitting all the data
    mean_nocensor_list = []  # list of means for fitting excluding censored data
    mean_censor_list = []  # list of means for fitting using censoring
    lengths = distr.rvs(scale=std, loc=mean, size=n_lines)
    sample_mean = np.mean(lengths)
    # lengths[np.where(lengths < 0)] *= -1  # flip to positive negative ends

    lengths = np.delete(lengths, np.where(lengths < 0))

    starts = np.zeros_like(lengths)

    ends = starts+lengths

    minimum_start = min(starts)  # Min start value
    maximum_end = max(ends) # Max end value

    dataset = pd.DataFrame({'starts': starts, 'ends': ends, 'og': lengths, 'modified': lengths, 'censored': np.zeros_like(lengths)})
    n_total = len(dataset)

    censoring_list = ss.uniform.rvs(size=len(lengths), random_state=numpy_randomGen)  # Values where we censor the data

    shift_window = np.linspace(0, maximum_end, n_windows)

    for shift in shift_window:
        censoring_values = censoring_list+shift
        for index, censoring_value in enumerate(censoring_values):
            if dataset['ends'][index] >= censoring_value:

                dataset.loc[dataset.index == index, 'censored'] = 1  # Flag the values > than the censoring value
                dataset.loc[dataset.index == index, 'modified'] = censoring_value  # Set the flagged value equal to the censoring value

        censored = dataset.loc[dataset['censored'] == 1, 'modified']  # Get censored values
        uncensored = dataset.loc[dataset['censored'] == 0, 'modified']  # Get uncensored values

        n_censored = len(censored)  # number of censored values
        # print(n_censored)
        # plot_survival(starts, ends, censoring_values)

        percentage_censored = 100*(n_censored/n_total)
        percentage_censoring_list.append(percentage_censored)

        # Fit everything

        params_all = distr.fit(dataset['modified'])
        fitted_all = distr(*params_all)
        mean_everything_list.append(fitted_all.mean()-sample_mean)

        # Fit only non censored

        if len(uncensored) == 0:
            mean_nocensor_list.append(np.nan)
        else:
            params_nocens = distr.fit(uncensored)
            fitted_nocens = distr(*params_nocens)
            mean_nocensor_list.append(fitted_nocens.mean()-sample_mean)

        # Fit with censoring

        ss_dataset = ss.CensoredData(uncensored=uncensored, right=censored)

        params_cens = distr.fit(ss_dataset)
        fitted_cens = distr(*params_cens)
        mean_censor_list.append(fitted_cens.mean()-sample_mean)

        dataset['modified'] = dataset['og']  # Reset the values
        dataset['censored'] = 0  # Reset the censoring flag

    iter_mean_everything_list[i, :] = mean_everything_list
    iter_mean_nocensor_list[i, :] = mean_nocensor_list
    iter_mean_censor_list[i, :] = mean_censor_list
    iter_percentage_censoring_list[i, :] = percentage_censoring_list


fig, ax = plt.subplots()


mean_of_means_everything = np.mean(iter_mean_everything_list, axis=0)
mean_of_means_nocensor = np.mean(iter_mean_nocensor_list, axis=0)
mean_of_means_censor = np.mean(iter_mean_censor_list, axis=0)
mean_of_percentage = np.mean(iter_percentage_censoring_list, axis=0)

# print(iter_percentage_censoring_list)
# print(mean_of_percentage)


for i in range(n_iterations):
    if i == 0:
        ax.plot(iter_percentage_censoring_list[i], iter_mean_everything_list[i], color='r', alpha=0.2, label='Fit all the data')
        ax.plot(iter_percentage_censoring_list[i], iter_mean_nocensor_list[i], color='b', alpha=0.2, label='Fit only complete data')
        ax.plot(iter_percentage_censoring_list[i], iter_mean_censor_list[i], color='g', alpha=0.2, label='Fit using survival')
    else:
        ax.plot(iter_percentage_censoring_list[i], iter_mean_everything_list[i], color='r', alpha=0.2)
        ax.plot(iter_percentage_censoring_list[i], iter_mean_nocensor_list[i], color='b', alpha=0.2)
        ax.plot(iter_percentage_censoring_list[i], iter_mean_censor_list[i], color='g', alpha=0.2)


# ax.plot(mean_of_percentage, mean_of_means_everything, color='r', label='Fit all the data')
# ax.plot(mean_of_percentage, mean_of_means_nocensor, color='b', label='Fit only complete data')
# ax.plot(mean_of_percentage, mean_of_means_censor, color='g', label='Fit using survival')

# ax.hlines(y=mean, xmin=0, xmax=100,
#            colors='k', label='True mean')
# ax.fill_between(mean_of_percentage, mean-std, mean+std, alpha=0.2)

ax.set_xlabel('% censored')
ax.set_ylabel('Estimated mean - Sample mean')
ax.set_ylim([-(mean+std+3), mean+std+3])
ax.legend()
plt.show()
