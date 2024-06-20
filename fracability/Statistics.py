import numpy as np

from numpy import exp
from numpy import log as ln
import pandas as pd
from pandas import DataFrame
import scipy.stats as ss
from scipy.optimize import minimize

from fracability.utils.general_use import KM
import fracability.Plotters as plotter


class NetworkData:

    """ Class used to represent fracture or fracture network data.
    It acts as a wrapper for the scipy CensoredData class

    :param obj: fracture/fracture network object
    :param use_survival: Use survival analysis to get the distribution. If false the whole dataset is used considering all fractures complete
    :param complete_only: When not using survival, use only the complete length values
    """

    def __init__(self, obj=None, use_survival=True, complete_only=True):


        self._obj = obj  # fracture/fracture network object

        self._data = None  # the data
        self._lengths: np.ndarray  # array of all the lengths (both complete and censored)
        self._non_censored_lengths: np.ndarray  # array of only complete lengths
        self._censored_lengths: np.ndarray  # array of only censored lengths
        self._ecdf: np.ndarray
        self._function_list: list = ['pdf', 'cdf', 'sf', 'hf', 'chf']  # list of possible functions

        self.use_survival = use_survival
        self.complete_only = complete_only

        if obj is not None:
            if self._obj.name == 'FractureNetwork':
                frac_obj = self._obj.fractures
            else:
                frac_obj = self._obj

            entity_df = frac_obj.entity_df
            entity_df = entity_df.sort_values(by='length')

            self.delta = 1-entity_df['censored'].values
            self._lengths = entity_df['length'].values
            self._non_censored_lengths = entity_df.loc[entity_df['censored'] == 0, 'length'].values
            self._censored_lengths = entity_df.loc[entity_df['censored'] == 1, 'length'].values
            self._ecdf = KM(self._lengths, self._lengths, self.delta)

            if self.use_survival:
                self.data = ss.CensoredData(uncensored=self._non_censored_lengths, right=self._censored_lengths)
            else:
                if self.complete_only:
                    self.data = self.non_censored_lengths
                else:
                    self.delta[:] = 1
                    self.data = self.lengths

    @property
    def data(self):
        """
        Property that returns or sets the CensoredData class of the fracture network
        :return:
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def lengths(self) -> np.ndarray:

        """
        This property returns or sets the complete list of length data (censored and uncesored) for the fracture network

        :getter: Return the complete list of lengths
        :setter: Set the complete list of lengths
        """

        return self._lengths

    @property
    def non_censored_lengths(self) -> np.ndarray:

        """
        This property returns or sets the list of non-censored length data of the fracture network

        :getter: Return the list of non-censored data
        :setter: Set the list of non-censored data
        """

        return self._non_censored_lengths

    @property
    def censored_lengths(self) -> np.ndarray:

        """
        This property returns or sets the list of censored length data of the fracture network

        :getter: Return the list of censored data
        :setter: Set the list of censored data
        :return:
        """

        return self._censored_lengths

    @property
    def function_list(self) -> list:
        """
        Property that returns the list of available probability functions (pdf, cdf etc)
        :return:
        """
        return self._function_list

    @property
    def mean(self) -> np.ndarray:
        """
        Calculate the sample mean of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample mean
        """
        return np.mean(self.lengths)

    @property
    def std(self) -> np.ndarray:
        """
        Calculate the sample standard deviation of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample standard deviation
        """
        return np.std(self.lengths)

    @property
    def var(self) -> np.ndarray:
        """
        Calculate the sample variance of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample variance
        """
        return np.var(self.lengths)

    @property
    def median(self) -> np.ndarray:
        """
        Calculate the sample median of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample median
        """
        return np.median(self.lengths)

    @property
    def mode(self) -> tuple:
        """
        Calculate the sample mode of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Tuple of the most frequent value(s)
        """
        return ss.mode(self.lengths)

    @property
    def b5(self) -> np.ndarray:
        """
        Calculate the sample 5th percentile of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample 5th percentile
        """
        return np.percentile(self.lengths, 5)

    @property
    def b95(self) -> np.ndarray:
        """
        Calculate the sample 95th percentile of ALL the input data (i.e. it ignores the complete_only flag).
        :return: Numpy array of the sample 95th percentile
        """
        return np.percentile(self.lengths, 95)

    @property
    def ecdf(self) -> np.ndarray:
        """
        Property that returns the empirical CDF of the input data (it ignores the complete_only flag but ) using Kaplan-Meier.
        :return: Numpy array of the calculated CDF values using KM
        """
        return self._ecdf

    @property
    def esf(self) -> np.ndarray:
        """
        Property that returns the empirical SF of the ALL the input data (i.e. it ignores the complete_only flag) using Kaplan-Meier.
        :return: Numpy array of the calculated SF values using KM
        """
        return 1-self.ecdf

    @property
    def total_n_fractures(self) -> int:
        """
        Total number of fractures of ALl the input data (i.e. it ignores the complete_only flag)
        :return: Int. Number of fractures
        """
        return len(self.lengths)

    @property
    def censoring_percentage(self) -> float:
        """
        Percentage of censoring of ALl the input data (i.e. it ignores the complete_only flag)
        :return: Float. Censoring %
        """
        return (len(self.censored_lengths)/self.total_n_fractures)*100


class NetworkDistribution:
    """
    Class used to represent a fracture or fracture network length distribution. It is essentially a wrapper for the
    scipy rv distributions.
    """

    def __init__(self, parent, obj: ss.rv_continuous = None, parameters: tuple = None, fit_data: NetworkData = None):

        self.parent: NetworkFitter = parent
        self._distribution = obj.freeze(*parameters)
        self.fit_data = fit_data

    @property
    def distribution(self) -> ss.rv_continuous:
        """
        Property that returns or sets a *frozen* ss.rv_continuous class
        :return:
        """
        return self._distribution

    @distribution.setter
    def distribution(self, distribution: ss.rv_continuous = None):
        self._distribution = distribution

    @property
    def distribution_name(self) -> str:
        """
        Property that returns the name of the given distribution
        :return:
        """
        return self.distribution.dist.name

    @property
    def distribution_parameters(self) -> tuple:
        """
        Property that returns the parameters of the frozen distribution
        :return:
        """
        return self.distribution.args

    @property
    def n_distribution_parameters(self) -> int:
        """
        Property that returns the number of parameters of the frozen distribution. the args method returns the
        shape parameters. This means that except for normal and logistic the loc counts as a parameter. To fix this we
        subtract -1 to all except normal and logistic.
        :return:
        """
        if self.distribution_name == 'norm' or self.distribution_name == 'logistic':

            return len(self.distribution_parameters)
        else:
            return len(self.distribution_parameters)-1

    @property
    def mean(self) -> float:
        """
        Property that returns the mean of the frozen distribution
        :return:
        """
        return self.distribution.mean()

    @property
    def mode(self) -> list:
        """
        Property that returns the mode(s) of the pdf of the given distribution
        :return:
        """
        return minimize(lambda x: -self.distribution.pdf(x), np.ceil(self.distribution_parameters[-1])).x

    @property
    def median(self) -> float:
        """
        Property that returns the median of the distribution
        :return:
        """
        return self.distribution.median()

    @property
    def var(self) -> float:
        """
        Property that returns the variance of the distribution
        :return:
        """
        return self.distribution.var()

    @property
    def std(self) -> float:
        """
        Property that returns the standard deviation of the distribution
        :return:
        """
        return self.distribution.std()

    @property
    def b5(self) -> float:
        """
        Property that returns the 5th percentile of the distribution
        :return:
        """
        return self.distribution.ppf(0.05)

    @property
    def b95(self) -> float:
        """
        Property that returns the 95th percentile of the distribution
        :return:
        """
        return self.distribution.ppf(0.95)

    def cdf(self, x_values: np.array = None):
        if x_values is not None:
            return self.distribution.cdf(x_values)
        else:
            return self.distribution.cdf(self.fit_data.lengths)

    def log_pdf(self, x_values: np.array = None) -> np.array:
        """
        Property that returns the logpdf calculated on the data
        :return:
        """

        if x_values.any():
            return self.distribution.logpdf(x_values)
        else:
            return np.array([0])

    def log_sf(self, x_values: np.array = None) -> np.array:
        """
        Property that returns the logsf calculated on the data
        :return:
        """
        if x_values.any():
            return self.distribution.logsf(x_values)
        else:
            return np.array([0])

    @property
    def max_log_likelihood(self) -> float:
        """
        Property that returns the log likelihood of the distribution. The likelihood is calculated by adding
        the cumulative sum of the log pdf and log sf of the fitted distribution.
        :return:
        """
        if self.fit_data.use_survival:
            log_f = self.log_pdf(self.fit_data.non_censored_lengths)
            log_r = self.log_sf(self.fit_data.censored_lengths)
        else:
            if self.fit_data.complete_only:
                sample = self.fit_data.non_censored_lengths
            else:
                sample = self.fit_data.lengths
            log_f = self.log_pdf(sample)
            log_r = np.array([0])

        LL_f = log_f.sum()
        LL_rc = log_r.sum()

        return LL_f + LL_rc

    # Distance parameters

    @property
    def AIC(self) -> float:
        """
        Property that returns the classic Akaike Information Criterion (1974) of the distribution
        :return:
        """
        max_log_likelihood = self.max_log_likelihood

        k = self.n_distribution_parameters

        AIC = (-2 * max_log_likelihood) + (2 * k)

        return AIC

    @property
    def AICc(self) -> float:
        """
        Property that returns the Akaike Information Criterion (for small number of values) of the distribution
        :return:
        """

        LL2 = -2 * self.max_log_likelihood

        k = self.n_distribution_parameters
        n = self.fit_data.total_n_fractures

        if (n - k - 1) == 0: # if n parameters + 1 = n of total fractures then the akaike is invalid i.e. the total fractures must be > than the n_parameters+1
            return -1
        else:
            AICc = 2 * k + LL2 + (2 * k ** 2 + 2 * k) / (n - k - 1)
            return AICc

    @property
    def Akaike_rank(self):
        fitter_records = self.parent.fit_records()
        name = self.distribution_name
        return fitter_records.loc[fitter_records['name'] == name, 'Akaike_rank'].values[0]

    @property
    def BIC(self) -> float:
        """
        Property that returns the Bayesian Information Criterion of the distribution
        :return:
        """
        LL2 = -2 * self.max_log_likelihood

        k = len(self.distribution_parameters)
        n = len(self.fit_data.non_censored_lengths) + len(self.fit_data.censored_lengths)

        BIC = np.log(n)*k + LL2
        return BIC

    @property
    def KS_distance(self) -> float:
        """
        Calcuate the Kolmogorov-Smirnov distance between the empirical and the fitted model
        :return: Float. The KS distance

        Notes
        ------
        Kim 2019, Tests based on EDF statistics for randomly censored normal
        distributions when parameters are unknown
        """
        Z = self.distribution.cdf(self.fit_data.lengths)
        G_n = self.fit_data.ecdf
        tot_n = self.fit_data.total_n_fractures
        delta = self.fit_data.delta

        complete_list_index = np.where(delta == 1)[0]
        diff_plus_list = []
        diff_minus_list = []

        for j in complete_list_index:
            diff_plus = G_n[j] - Z[j]  # Calculate the positive difference at index j (DC+)

            if j + 1 > tot_n - 1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
                Z_j1 = 1
            else:
                Z_j1 = Z[j + 1]

            diff_minus = Z_j1 - G_n[j]  # Calculate the negative difference at index j (DC-)
            diff_plus_list.append(diff_plus)
            diff_minus_list.append(diff_minus)

        DCn_pos = max(diff_plus_list)
        DCn_neg = max(diff_minus_list)

        DCn = max(DCn_pos, DCn_neg)

        return DCn

    @property
    def KS_rank(self):
        fitter_records = self.parent.fit_records()
        name = self.distribution_name
        return fitter_records.loc[fitter_records['name'] == name, 'KS_rank'].values[0]

    @property
    def KG_distance(self) -> float:
        """
        Calcuate the Koziol and Green distance between the empirical and the fitted model
        :return: Float. The KG distance

        Notes
        ------
        Kim 2019, Tests based on EDF statistics for randomly censored normal
        distributions when parameters are unknown
        """

        Z = self.distribution.cdf(self.fit_data.lengths)
        G_n = self.fit_data.ecdf
        tot_n = self.fit_data.total_n_fractures
        kg_sum = 0

        for j in range(tot_n):

            if j + 1 > tot_n - 1:  # Check if j+1 (0 indexed) is bigger than the total number tot_n (1 indexed)
                Z_j1 = 1
            else:
                Z_j1 = Z[j + 1]
            kg_sum += G_n[j] * (Z_j1 - Z[j]) * (G_n[j] - (Z_j1 + Z[j]))

        psi_sq = (tot_n * kg_sum) + tot_n / 3

        return psi_sq

    @property
    def KG_rank(self):
        fitter_records = self.parent.fit_records()
        name = self.distribution_name
        return fitter_records.loc[fitter_records['name'] == name, 'KG_rank'].values[0]

    @property
    def AD_distance(self) -> float:
        """
        Calcuate the Koziol and Green distance between the empirical and the fitted model
        :return: Float. The KG distance

        Notes
        ------
        Kim 2019, Tests based on EDF statistics for randomly censored normal
        distributions when parameters are unknown
        """
        smallest_number = 10**-10
        Z = self.distribution.cdf(self.fit_data.lengths)
        G_n = self.fit_data.ecdf
        tot_n = self.fit_data.total_n_fractures

        sum1 = 0  # First sum
        sum2 = 0  # Second sum
        if Z[-1] == 1:
            Z[-1] -= smallest_number  # this is to avoid 0 in ln(1 - Z[-1])
        elif Z[-1] == 0:
            Z[-1] += smallest_number  # this is to avoid 0 in ln(Z[-1])
        for j in range(tot_n - 1):

            if Z[j + 1] == 0:
                Z[j + 1] += smallest_number  # this is to avoid 0 in ln(Z[j + 1])
            elif Z[j + 1] == 1:
                Z[j + 1] -= smallest_number  # this is to avoid 0 in ln(1 - Z[j + 1])

            if Z[j] == 0:
                Z[j] += smallest_number  # this is to avoid 0 in ln(Z[j])
            elif Z[j] == 1:
                Z[j] -= smallest_number  # this is to avoid 0 in ln(1 - Z[j])

            sum1 += (G_n[j] ** 2) * (-ln(1 - Z[j + 1]) + ln(Z[j + 1]) + ln(1 - Z[j]) - ln(Z[j]))
            sum2 += G_n[j] * (-ln(1 - Z[j + 1]) + ln(1 - Z[j]))

        AC_sq = (tot_n * sum1) - (2 * tot_n * sum2) - (tot_n * ln(1 - Z[-1])) - (tot_n * ln(Z[-1])) - tot_n

        return AC_sq

    @property
    def AD_rank(self):
        fitter_records = self.parent.fit_records()
        name = self.distribution_name
        return fitter_records.loc[fitter_records['name'] == name, 'AD_rank'].values[0]

    @property
    def Mean_rank(self):
        fitter_records = self.parent.fit_records()
        name = self.distribution_name
        return fitter_records.loc[fitter_records['name'] == name, 'Mean_rank'].values[0]


class NetworkFitter:

    """
    Class used to fit a Fracture or Fracture network object

    :param obj: fracture/fracture network object
    :param use_survival: Boolean flag to use survival (True) or treat the data as if there were no censoring (False). Default is True.
    :param complete_only: Boolean flag to use only complete measurements (True) or all the dataset (False). This flag is used only when use_survival is False. Default is False.
    :param use_AIC: Boolean flag to use AIC (True) or AICc (False) for model selection. Default is True. The
    column name in the dataframe will remain the same (Akaike).

    Add bool to:
        + Consider censored lengths as non-censored
        + Do not consider censored lengths at all

    """
    def __init__(self, obj=None, use_survival=True, complete_only=False, use_AIC=True):

        self._net_data: NetworkData
        self._accepted_fit: list = []
        self._rejected_fit: list = []
        self._AIC_flag: bool = use_AIC
        self._fit_dataframe: DataFrame = DataFrame(columns=['name', 'Akaike',
                                                            'delta_i', 'w_i',
                                                            'max_log_likelihood', 'KS_distance',
                                                            'KG_distance', 'AD_distance',
                                                            'Akaike_rank', 'KS_rank',
                                                            'KG_rank', 'AD_rank',
                                                            'Mean_rank', 'distribution'])

        self.network_data = NetworkData(obj, use_survival, complete_only)

    @property
    def network_data(self) -> NetworkData:
        """
        Property that returns or sets a NetworkData object
        :return:
        """
        return self._net_data

    @network_data.setter
    def network_data(self, data: NetworkData):
        self._net_data = data

    def fit(self, distribution_name: str):

        """
        Fit the data of the entity_df using scipy available distributions
        :param distribution_name: Name of the distribution to fit
        :return:
        """
        print(f'Fitting {distribution_name} on data')
        last_pos = len(self._fit_dataframe)  # The position of a new entry in the dataframe will be the last (i.e. the length of the dataframe)

        self._fit_dataframe.loc[last_pos, 'name'] = distribution_name

        scipy_distribution = getattr(ss, distribution_name)

        if distribution_name == 'norm' or distribution_name == 'logistic':
            params = scipy_distribution.fit(self.network_data.data)
        else:
            params = scipy_distribution.fit(self.network_data.data, floc=0)

        distribution = NetworkDistribution(parent=self, obj=scipy_distribution,
                                           parameters=params, fit_data=self.network_data)

        if self._AIC_flag:
            akaike = distribution.AIC
        else:
            akaike = distribution.AICc

        self._fit_dataframe.loc[last_pos, 'Akaike'] = akaike

        log_likelihood = distribution.max_log_likelihood

        self._fit_dataframe.loc[last_pos, 'max_log_likelihood'] = log_likelihood
        for i, AIC_val in enumerate(self._fit_dataframe['Akaike']):
            d_i = AIC_val - min(self._fit_dataframe['Akaike'])
            self._fit_dataframe.loc[i, 'delta_i'] = d_i
        delta_values = (-self._fit_dataframe['delta_i'].values/2).astype(float)
        total = exp(delta_values).sum()

        for d, delta_i in enumerate(self._fit_dataframe['delta_i']):
            w_i = np.round(exp(-delta_i/2)/total, 5)
            self._fit_dataframe.loc[d, 'w_i'] = w_i

        self._fit_dataframe.loc[last_pos, 'KS_distance'] = distribution.KS_distance
        self._fit_dataframe.loc[last_pos, 'KG_distance'] = distribution.KG_distance
        self._fit_dataframe.loc[last_pos, 'AD_distance'] = distribution.AD_distance

        self._fit_dataframe['Akaike_rank'] = ss.rankdata(self._fit_dataframe['Akaike']).astype(int)
        self._fit_dataframe['KS_rank'] = ss.rankdata(self._fit_dataframe['KS_distance']).astype(int)
        self._fit_dataframe['KG_rank'] = ss.rankdata(self._fit_dataframe['KG_distance']).astype(int)
        self._fit_dataframe['AD_rank'] = ss.rankdata(self._fit_dataframe['AD_distance']).astype(int)
        self._fit_dataframe['Mean_rank'] = self._fit_dataframe.iloc[:, 8:12].mean(axis=1)

        self._fit_dataframe.loc[last_pos, 'distribution'] = distribution

        # self._fit_dataframe.loc[last_pos, 'params'] = params  # this gives out an error for setting the df, I do not know why

    def fit_records(self, sort_by='Akaike') -> DataFrame:

        """ Return the sorted fit dataframe"""

        return self._fit_dataframe.sort_values(by=sort_by, ignore_index=True)

    def get_fitted_distribution(self, distribution_name: str, sort_by='Akaike') -> NetworkDistribution:

        """
        get the fitted NetworkDistribution object
        :param distribution_name: name of the distribution
        :param sort_by: Column name to sort the output order
        :return:
        """
        fit_records = self.fit_records(sort_by)
        distribution = fit_records.loc[fit_records['name'] == distribution_name, 'distribution'].values[0]

        return distribution

    def get_fitted_distribution_names(self, sort_by='Akaike') -> list:

        """
        get the names of the fitted NetworkDistribution object
        :param sort_by: Column name to sort the output order
        :return:
        """

        return self.fit_records(sort_by)['name'].values

    def get_fitted_distribution_list(self, distribution_names: list = None, sort_by='Akaike') -> list:
        """
        Get a list of NetworkDistribution objects for the given distribution name
        :param distribution_names:
        :param sort_by: Column name to sort the output order
        :return:
        """
        fit_records = self.fit_records(sort_by)
        if distribution_names is None:
            distribution_names = fit_records['name'].tolist()

        distribution_list = []

        for name in distribution_names:
            distribution = fit_records.loc[fit_records['name'] == name, 'distribution'].values[0]
            distribution_list.append(distribution)

        return distribution_list

    def get_fitted_parameters(self, distribution_name: str, sort_by='Akaike') -> tuple:
        """
        Get the fitted distributions parameters in the fit records df
        :param distribution_name: Name of the distribution
        :param sort_by: Column name to sort the output order
        """
        fit_records = self.fit_records(sort_by)
        dist = fit_records.loc[fit_records['name'] == distribution_name, 'distribution'].values[0]
        parameters = dist.distribution_parameters
        return parameters

    def get_fitted_parameters_list(self, distribution_names: list = None, sort_by='Akaike') -> list:

        """
        Get the parameters of the computed fit(s)
        :return: Pandas DataFrame
        """

        fit_records = self.fit_records(sort_by)

        if distribution_names is None:
            distribution_names = fit_records['name'].tolist()

        parameter_list = []

        for name in distribution_names:
            parameter_list.append(self.get_fitted_parameters(name))

        return parameter_list

    def best_fit(self, sort_by='Akaike') -> pd.Series:

        """
        Return the best fit in the fit records dataframe sorted by sort_by
        :return:
        """

        df = self.fit_records(sort_by)

        return df.loc[0]

    # ====================== Plot ==========================

    def plot_PIT(self,  show_plot: bool = True,
                 position: list = None, sort_by: str = 'Akaike',
                 bw: bool = False,
                 second_axis: bool = True,
                 n_ticks: int = 5):
        """
        Method to plot the uniform comparison plot for the fitted models.

        :param show_plot: Bool. If True, show the plot if False do not show. Default is True.
        :param position: List. Plot the models at the given position in the ordered fit_records dataframe. If None (default) plot all models.
        :param sort_by: String. Column name to sort the fit_records dataframe. Default is Akaike
        :param bw: Bool. If true turn the plot color-blind friendly (black lines with different patterns). Max 7 lines (i.e. models). Default is False
        :param second_axis: Add the secondary x-axis to the PIT plot
        :param n_ticks: Number of ticks for the secondary x-axis
        :return:
        """

        plotter.matplot_stats_uniform(self, show_plot, position, sort_by, bw, second_axis, n_ticks)

    def tick_plot(self, show_plot: bool = True,
                  position: list = None, n_ticks: int = 5,
                  sort_by: str = 'Akaike'):
        """
        Method used to plot the tick plot of the given fitted model(s)
        :param show_plot: Bool. If True, show the plot if False do not show. Default is True.
        :param position: List. Plot the models at the given position in the ordered fit_records dataframe. If None (default) plot all models.
        :param n_ticks: Number of ticks per bar
        :param sort_by: String. Column name to sort the fit_records dataframe. Default is Akaike
        :return:
        """

        plotter.matplot_tick_plot(self, show_plot=show_plot, position=position, n_ticks=n_ticks, sort_by=sort_by)

    def plot_summary(self, show_plot:bool = True, position: list = None, sort_by: str = 'Akaike'):
        """
        Method to plot the summary plot for the given fitted model(s).
        :param show_plot: Bool. If True, show the plot if False do not show. Default is True.
        :param position: List. Plot the models at the given position in the ordered fit_records dataframe. If None (default) plot all models.
        :param sort_by: String. Column name to sort the fit_records dataframe. Default is Akaike
        :return:
        """

        plotter.matplot_stats_summary(self, show_plot=show_plot, position=position, sort_by=sort_by)

    # ====================== Export ==========================
    def fit_result_to_csv(self, path, sort_by='Akaike'):
        """
        Save the csv to a specified path
        :param path: Path of where to save the csv
        :param sort_by: Column name to sort the values
        :return:
        """
        self.fit_records(sort_by).iloc[:, :-1].to_csv(path, sep=';', index=False)

    def fit_result_to_excel(self, path, sort_by='Akaike'):
        """
        Save the excel to a specified path
        :param path: Path of where to save the excel
        :param sort_by: Column name to sort the values
        :return:
        """
        self.fit_records(sort_by).iloc[:, :-1].to_excel(path, index=False)

    def fit_result_to_clipboard(self, sort_by='Akaike'):
        """
        Copy to clipboard the df to be easily pasted in an excel file
        :param sort_by: Column name to sort the values
        :return:
        """
        self.fit_records(sort_by).iloc[:, :-1].to_clipboard(index=False)

    # def plot_kde(self, n_bins: int = 25, x_min: float = 0.0, x_max: float = None, res: int = 1000):
    #
    #     """
    #     Plot the Kernel Density Estimation PDF function togather with the data histogram
    #
    #     Parameters
    #     -------
    #     n_bins: Number of histogram bins
    #
    #     x_min: Lower value of the range. By default is set to 0
    #
    #     x_max: Higher value of the range. If None the maximum length of the dataset is used. None by default
    #
    #     res: Point resolution between x_min and x_max. By default is set to 1000
    #
    #     """
    #
    #     data = self._lengths
    #
    #     if x_max is None:
    #         x_max = self._lengths.max()
    #
    #     x_vals = np.linspace(x_min, x_max, res)
    #
    #     pdf_kde = gaussian_kde(data).evaluate(x_vals)
    #
    #     fig = plt.figure(num='Gaussian KDE estimation')
    #     plt.hist(data, density=True, bins=15,label='Data')
    #     plt.plot(x_vals, pdf_kde, label='Gaussian KDE')
    #
    #     plt.title('Gaussian KDE estimation')
    #     plt.xlabel('Length [m]')
    #     plt.ylabel('Function response')
    #     plt.grid(True)
    #     plt.show()