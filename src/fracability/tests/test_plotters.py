from fracability.examples import example_fracture_network
import pytest
from fracability.Entities import FractureNetwork
from fracability.operations.Statistics import NetworkFitter
import matplotlib.pyplot as plt


@pytest.fixture(scope="session", autouse=True)
def environment_var():
    data = example_fracture_network.fracture_net_components()
    pytest.fracture_net = FractureNetwork(data)
    pytest.fitter = NetworkFitter(pytest.fracture_net)
    pytest.dist = 'lognorm'
    pytest.fitter.fit(pytest.dist)


class TestMatplot:

    def test_matplot_nodes(self):
        nodes = pytest.fracture_net.nodes
        assert 'n_type' in nodes.entity_df.columns
        ax = matplot_nodes(nodes, markersize=5, return_plot=True)
        assert ax
        plt.close()

    def test_matplot_fractures(self):
        fractures = pytest.fracture_net.fractures

        # matplot_fractures(fractures, linewidth=2, color='red', color_set=False, return_plot=False, show_plot=False)
        # matplot_fractures(fractures, linewidth=2, color='red', color_set=True, return_plot=False, show_plot=False)

        ax = matplot_fractures(fractures, linewidth=2, color='red', color_set=False, return_plot=True)
        assert ax
        plt.close()
        assert 'f_set' in fractures.entity_df.columns
        ax = matplot_fractures(fractures, linewidth=2, color='red', color_set=True, return_plot=True)
        assert ax
        plt.close()

    def test_matplot_boundaries(self):
        boundaries = pytest.fracture_net.boundaries
        # matplot_boundaries(boundaries, linewidth=2, color='red', return_plot=False, show_plot=False)
        assert 'b_group' in boundaries.entity_df.columns
        ax = matplot_boundaries(boundaries, linewidth=2, color='red', return_plot=True)
        assert ax
        plt.close()

    def test_matplot_fracture_net(self):
        fracture_net = pytest.fracture_net
        # matplot_frac_net(fracture_net, markersize=6, linewidth=[1, 2], color=['black', 'black'],
        #                  color_set=False, return_plot=False, show_plot=False)
        # matplot_frac_net(fracture_net, markersize=6, linewidth=[1, 2], color=['black', 'black'],
        #                  color_set=True, return_plot=False, show_plot=True)

        ax = matplot_frac_net(fracture_net, markersize=6, linewidth=[1, 2], color=['black', 'black'],
                              color_set=False, return_plot=True, show_plot=False)
        assert ax
        plt.close()

        ax = matplot_frac_net(fracture_net, markersize=6, linewidth=[1, 2], color=['black', 'black'],
                              color_set=True, return_plot=True, show_plot=False)
        assert ax
        plt.close()

    def test_matplot_ternary(self):
        fracture_net = pytest.fracture_net
        nodes = pytest.fracture_net.nodes

        ax_frac = matplot_ternary(fracture_net, return_plot=True, show_plot=False)
        ax_nodes = matplot_ternary(nodes, return_plot=True, show_plot=False)

        assert ax_frac
        assert ax_nodes


class TestMatplotStats:

    def test_matplot_stats_pdf(self):
        matplot_stats_pdf(pytest.fitter.get_fitted_distribution(pytest.dist),
                          histogram=False,
                          show_plot=False)
        matplot_stats_pdf(pytest.fitter.get_fitted_distribution(pytest.dist),
                          histogram=True,
                          show_plot=False)

        # ax = matplot_stats_pdf(pytest.fitter.get_fitted_distribution(pytest.dist),
        #                        histogram=False,
        #                        show_plot=False)
        # ax_hist = matplot_stats_pdf(pytest.fitter.get_fitted_distribution(pytest.dist),
        #                             histogram=False,
        #                             show_plot=False)
        #
        # assert ax
        # plt.close()
        # assert ax_hist
        # plt.close()

    def test_matplot_stats_cdf(self):
        matplot_stats_cdf(pytest.fitter.get_fitted_distribution(pytest.dist), plot_ecdf=False, show_plot=False)
        matplot_stats_cdf(pytest.fitter.get_fitted_distribution(pytest.dist), plot_ecdf=True, show_plot=False)

    def test_matplot_stats_sf(self):
        matplot_stats_sf(pytest.fitter.get_fitted_distribution(pytest.dist), plot_esf=False, show_plot=False)
        matplot_stats_sf(pytest.fitter.get_fitted_distribution(pytest.dist), plot_esf=True, show_plot=False)

    def test_matplot_stats_table(self):
        matplot_stats_table(pytest.fitter.get_fitted_distribution(pytest.dist), vertical=False, show_plot=False)
        matplot_stats_table(pytest.fitter.get_fitted_distribution(pytest.dist), vertical=True, show_plot=False)

    def test_matplot_stats_summary(self):
        matplot_stats_summary(pytest.fitter.get_fitted_distribution(pytest.dist), table=False, show_plot=False)
        matplot_stats_summary(pytest.fitter.get_fitted_distribution(pytest.dist), table=True, show_plot=False)


class TestVTKPlot:

    def test_vtkplot_nodes(self):
        nodes = pytest.fracture_net.nodes
        # vtkplot_nodes(nodes, markersize=5, return_plot=False, show_plot=False)

        assert 'n_type' in nodes.vtk_object.array_names
        assert vtkplot_nodes(nodes, markersize=5, return_plot=True, show_plot=False)

    def test_vtkplot_fractures(self):
        fractures = pytest.fracture_net.fractures
        # vtkplot_fractures(fractures, linewidth=2, color='black', color_set=False, return_plot=False, show_plot=False)
        # vtkplot_fractures(fractures, linewidth=2, color='white', color_set=True, return_plot=False, show_plot=False)
        assert 'f_set' in fractures.vtk_object.array_names
        assert vtkplot_fractures(fractures, linewidth=2, color='white',
                                 color_set=False, return_plot=True, show_plot=False)
        assert vtkplot_fractures(fractures, linewidth=2, color='white',
                                 color_set=True, return_plot=True, show_plot=False)

    def test_vtkplot_boundaries(self):
        boundaries = pytest.fracture_net.boundaries
        # vtkplot_boundaries(boundaries, linewidth=2, color='red', return_plot=False, show_plot=False)
        assert 'b_group' in boundaries.vtk_object.array_names
        assert vtkplot_boundaries(boundaries, linewidth=2, color='white', return_plot=True, show_plot=False)

    def test_vtkplot_frac_net(self):

        fracture_net = pytest.fracture_net

        # vtkplot_frac_net(fracture_net, markersize=5, linewidth=[1, 2], color=['black', 'white'],
        #                  color_set=False, return_plot=False, show_plot=False)
        #
        # vtkplot_frac_net(fracture_net, markersize=5, linewidth=[1, 2], color=['black', 'white'],
        #                  color_set=True, return_plot=False, show_plot=False)

        assert vtkplot_frac_net(fracture_net, markersize=5, linewidth=[1, 2], color=['black', 'white'],
                                 color_set=False, return_plot=True, show_plot=False)

        assert vtkplot_frac_net(fracture_net, markersize=5, linewidth=[1, 2], color=['black', 'white'],
                                 color_set=True, return_plot=True, show_plot=False)
