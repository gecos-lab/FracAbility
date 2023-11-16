import numpy as np


def ecdf(uncensored = None, censored = None):
    """
    Calculate the empirical cdf of a given dataset with right censoring (if present)

    This function is copied from https://github.com/scipy/scipy/blob/1305da5985cbb1524aaa58b1296647bb122e6249/scipy/stats/_survival.py#L432
    waiting for the new scipy 1.11 release.

    :param uncensored:
    :param censored:
    :return:
    """

    tod = np.array(uncensored)
    tol = np.array(censored)
    times = np.concatenate((tod, tol))
    died = np.asarray([1] * tod.size + [0] * tol.size)

    # sort by times
    i = np.argsort(times)
    times = times[i]
    died = died[i]
    at_risk = np.arange(times.size, 0, -1)

    # logical indices of unique times
    j = np.diff(times, prepend=-np.inf, append=np.inf) > 0
    j_l = j[:-1]  # first instances of unique times
    j_r = j[1:]  # last instances of unique times

    # get number at risk and deaths at each unique time
    t = times[j_l]  # unique times
    n = at_risk[j_l]  # number at risk at each unique time
    cd = np.cumsum(died)[j_r]  # cumulative deaths up to/including unique times
    d = np.diff(cd, prepend=0)  # deaths at each unique time

    # compute survival function
    sf = np.cumprod((n - d) / n)
    cdf = 1 - sf
    cdf = np.insert(cdf, 0, 0)

    return times, cdf

