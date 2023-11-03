"""

Test survival analysis feasibility for single censored events.

1. Every event starts at the same point
2. Every event has a randomly distributed end following a normal distribution
3. Every event is censored at the same value

We test the effects of the % censoring on the fitting of a known distribution by plotting the % of censored values
with the estimated mean.


THIS MAKES NO SENSE. Because we need to distribute the lengths and not the ends of a measure.
"""

import scipy.stats as ss
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

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


mean = 10
std = 4
n_lines = 10

percentage_censoring_list = []
mean_everything_list = []  # list of means for fitting all the data
mean_nocensor_list = []  # list of means for fitting excluding censored data
mean_censor_list = []  # list of means for fitting using censoring

n_windows = 10  # number of windows used to censor the values

ends = ss.norm.rvs(loc=mean, scale=std, size=n_lines)
ends[np.where(ends < 0)] *= -1  # flip to positive negative ends
starts = np.zeros_like(ends)

minimum_start = min(starts)  # Min start value
maximum_end = max(ends) # Max end value

plot_survival(starts, ends)

lengths = ends-starts

dataset = pd.DataFrame({'og': lengths, 'modified': lengths, 'censored': np.zeros_like(lengths)})
n_total = len(dataset)

censoring_values = np.linspace(0.1, maximum_end*1.05, n_windows)  # Values where we censor the data


for censoring_value in censoring_values:
    dataset.loc[dataset['modified'] >= censoring_value, 'censored'] = 1  # Flag the values > than the censoring value
    dataset.loc[dataset['censored'] == 1, 'modified'] = censoring_value  # Set the flagged value equal to the censoring value
    censored = dataset.loc[dataset['censored'] == 1, 'modified']  # Get censored values
    uncensored = dataset.loc[dataset['censored'] == 0, 'modified']  # Get uncensored values

    n_censored = len(censored)  # number of censored values

    percentage_censored = 100*(n_censored/n_total)
    percentage_censoring_list.append(percentage_censored)

    # Fit everything

    mean_all, std_all = ss.norm.fit(dataset['modified'])
    mean_everything_list.append(mean_all)

    # Fit only non censored

    mean_nocens, std_nocens = ss.norm.fit(uncensored)
    mean_nocensor_list.append(mean_nocens)

    # Fit with censoring

    ss_dataset = ss.CensoredData(uncensored=uncensored, right=censored)

    mean_cens, std_cens = ss.norm.fit(ss_dataset)
    mean_censor_list.append(mean_cens)

    dataset['modified'] = dataset['og']  # Reset the values
    dataset['censored'] = 0  # Reset the censoring flag


fig, ax = plt.subplots()
ax.plot(percentage_censoring_list, mean_everything_list, color='r', label='all')
ax.plot(percentage_censoring_list, mean_nocensor_list, color='b', label='no cens')
ax.plot(percentage_censoring_list, mean_censor_list, color='g', label='cens')
ax.hlines(y=mean, xmin=min(percentage_censoring_list), xmax=max(percentage_censoring_list),
           colors='k', label='True mean')

ax.fill_between(percentage_censoring_list, mean-std, mean+std, alpha=0.2)

ax.set_xlabel('% censored')
ax.set_ylabel('Mean')
ax.legend()
plt.show()