import networkx
import pytest
import pyvista

import os
import glob

from fracability.Entities import Nodes, Fractures, Boundary, FractureNetwork
from fracability.examples import example_fracture_network


class TestNodes:
    """
    Class used to test Node entity creation
    """

    def test_creation(self):
        data = example_fracture_network.fracture_net_components()
        pytest.nodes_data = data.loc[data['type'] == 'node']

        assert isinstance(Nodes(gdf=pytest.nodes_data), Nodes)

        pytest.nodes = Nodes(gdf=pytest.nodes_data)

    def test_entity_df(self):
        assert not pytest.nodes.entity_df.empty

    def test_set_entity_df(self):
        pytest.nodes.entity_df = pytest.nodes_data

        assert pytest.nodes.entity_df.equals(pytest.nodes_data)

    def test_vtk_object(self):
        assert isinstance(pytest.nodes.vtk_object, pyvista.PolyData)

        vtk_obj = pytest.nodes.vtk_object
        assert 'type' in vtk_obj.array_names
        assert 'n_type' in vtk_obj.array_names

    def test_network_object(self):
        assert isinstance(pytest.nodes.network_object, networkx.Graph)

    def test_save_csv(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_nodes_csv.csv')
        pytest.nodes.save_csv(file_path)
        assert os.path.isfile(file_path)
        os.remove(file_path)

    def test_save_shp(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_nodes_shp.shp')
        pytest.nodes.save_shp(file_path)
        assert os.path.isfile(file_path)
        paths = glob.glob(os.path.join(cwd, 'test_nodes_shp.*'))
        for path in paths:
            os.remove(path)

    def test_crs(self):
        assert pytest.nodes.crs is not None


class TestFractures:
    """
    Class used to test Fracture entity creation
    """

    def test_creation_components_df(self):
        data = example_fracture_network.fracture_net_components()
        pytest.fracture_data = data.loc[data['type'] == 'fracture']

        assert isinstance(Fractures(gdf=pytest.fracture_data), Fractures)
        pytest.fractures = Fractures(pytest.fracture_data)

        set_1_data = pytest.fracture_data.loc[pytest.fracture_data['f_set'] == 1]
        set_2_data = pytest.fracture_data.loc[pytest.fracture_data['f_set'] == 2]

        assert isinstance(Fractures(gdf=set_1_data, set_n=1), Fractures)
        assert isinstance(Fractures(gdf=set_2_data, set_n=2), Fractures)
        assert all(Fractures(gdf=set_1_data, set_n=1).entity_df['f_set'] == 1)
        assert all(Fractures(gdf=set_2_data, set_n=2).entity_df['f_set'] == 2)

        pytest.fractures_1 = Fractures(gdf=set_1_data, set_n=1)
        pytest.fractures_2 = Fractures(gdf=set_2_data, set_n=2)

    def test_creation_shp(self):
        shp_path, _ = example_fracture_network.fracture_net_subset()

        assert isinstance(Fractures(shp=shp_path['fractures']), Fractures)
        assert isinstance(Fractures(shp=shp_path['set_1'], set_n=1), Fractures)
        assert isinstance(Fractures(shp=shp_path['set_2'], set_n=2), Fractures)

        fractures = Fractures(shp=shp_path['fractures'])
        set_1 = Fractures(shp=shp_path['set_1'], set_n=1)
        set_2 = Fractures(shp=shp_path['set_2'], set_n=2)

        assert not fractures.entity_df.empty
        assert not set_1.entity_df.empty
        assert not set_2.entity_df.empty

    def test_entity_df(self):
        assert not pytest.fractures.entity_df.empty

    def test_set_entity_df(self):
        pytest.fractures.entity_df = pytest.fracture_data

        assert pytest.fractures.entity_df.equals(pytest.fracture_data)

    def test_vtk_object(self):
        assert isinstance(pytest.fractures.vtk_object, pyvista.PolyData)

        vtk_obj = pytest.fractures.vtk_object
        assert 'type' in vtk_obj.array_names
        assert 'f_set' in vtk_obj.array_names
        assert 'RegionId' in vtk_obj.array_names

    def test_network_object(self):
        assert isinstance(pytest.fractures.network_object, networkx.Graph)

    def test_crs(self):
        assert pytest.fractures.crs is not None

    def test_save_csv(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_fractures_csv.csv')
        pytest.fractures.save_csv(file_path)
        assert os.path.isfile(file_path)
        os.remove(file_path)

    def test_save_shp(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_fractures_shp.shp')
        pytest.fractures.save_shp(file_path)
        assert os.path.isfile(file_path)
        paths = glob.glob(os.path.join(cwd, 'test_fractures_shp.*'))
        for path in paths:
            os.remove(path)


class TestBoundary:
    """
    Class used to test Boundary entity creation
    """

    def test_creation(self):
        data = example_fracture_network.fracture_net_components()
        pytest.boundary_data = data.loc[data['type'] == 'boundary']

        assert isinstance(Boundary(gdf=pytest.boundary_data), Boundary)

        pytest.boundaries = Boundary(gdf=pytest.boundary_data)

    def test_entity_df(self):
        assert not pytest.boundaries.entity_df.empty

    def test_set_entity_df(self):
        pytest.boundaries.entity_df = pytest.boundary_data

        assert pytest.boundaries.entity_df.equals(pytest.boundary_data)

    def test_vtk_object(self):
        assert isinstance(pytest.boundaries.vtk_object, pyvista.PolyData)

        vtk_obj = pytest.boundaries.vtk_object
        assert 'type' in vtk_obj.array_names
        assert 'RegionId' in vtk_obj.array_names

    def test_network_object(self):
        assert isinstance(pytest.boundaries.network_object, networkx.Graph)

    def test_save_csv(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_boundaries_csv.csv')
        pytest.boundaries.save_csv(file_path)
        assert os.path.isfile(file_path)
        os.remove(file_path)

    def test_save_shp(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_boundaries_shp.shp')
        pytest.boundaries.save_shp(file_path)
        assert os.path.isfile(file_path)
        paths = glob.glob(os.path.join(cwd, 'test_boundaries_shp.*'))
        for path in paths:
            os.remove(path)

    def test_crs(self):
        assert pytest.boundaries.crs is not None


class TestFractureNetwork:
    """
    Class used to test FractureNetwork entity creation
    """
    def test_add_nodes(self):
        fracture_net = FractureNetwork()
        fracture_net.add_nodes(pytest.nodes)
        assert 1 in set(fracture_net.entity_df['n_type'])
        assert 3 in set(fracture_net.entity_df['n_type'])
        assert 4 in set(fracture_net.entity_df['n_type'])
        assert 5 in set(fracture_net.entity_df['n_type'])
        assert 6 in set(fracture_net.entity_df['n_type'])

    def test_add_fractures(self):
        fracture_net = FractureNetwork()
        fracture_net.add_fractures(pytest.fractures)
        assert 1 in set(fracture_net.entity_df['f_set'])
        assert 2 in set(fracture_net.entity_df['f_set'])

    def test_add_fractures_set(self):
        fracture_net = FractureNetwork()
        fracture_net.add_fractures(pytest.fractures_1)
        fracture_net.add_fractures(pytest.fractures_2)
        assert 1 in set(fracture_net.entity_df['f_set'])
        assert 2 in set(fracture_net.entity_df['f_set'])

    def test_add_boundaries(self):
        fracture_net = FractureNetwork()
        fracture_net.add_boundaries(pytest.boundaries)
        assert 1 in set(fracture_net.entity_df['b_group'])

    def test_create_fn_df(self):
        fracture_net = FractureNetwork(example_fracture_network.fracture_net_components())

        assert not fracture_net.entity_df.empty
        assert not fracture_net.nodes.entity_df.empty
        assert not fracture_net.fractures.entity_df.empty
        assert not fracture_net.boundaries.entity_df.empty
        assert fracture_net.fracture_network_to_components_df().equals(
            example_fracture_network.fracture_net_components())

    def test_create_fn_add(self):

        pytest.fracture_net = FractureNetwork()
        pytest.fracture_net.add_nodes(pytest.nodes)
        pytest.fracture_net.add_fractures(pytest.fractures)
        pytest.fracture_net.add_boundaries(pytest.boundaries)

        assert not pytest.fracture_net.entity_df.empty
        assert not pytest.fracture_net.nodes.entity_df.empty
        assert not pytest.fracture_net.fractures.entity_df.empty
        assert not pytest.fracture_net.boundaries.entity_df.empty
        assert pytest.fracture_net.fracture_network_to_components_df().equals(
            example_fracture_network.fracture_net_components())

    def test_activate_nodes(self):
        pytest.fracture_net.activate_nodes([1, 4])

        assert pytest.fracture_net.is_type_active(1)
        assert pytest.fracture_net.is_type_active(4)
        assert not pytest.fracture_net.is_type_active(3)
        assert not pytest.fracture_net.is_type_active(5)
        assert not pytest.fracture_net.is_type_active(6)
        pytest.fracture_net.activate_nodes()

    def test_deactivate_nodes(self):
        pytest.fracture_net.deactivate_nodes([1, 4])

        assert not pytest.fracture_net.is_type_active(1)
        assert not pytest.fracture_net.is_type_active(4)
        assert pytest.fracture_net.is_type_active(3)
        assert pytest.fracture_net.is_type_active(5)
        assert pytest.fracture_net.is_type_active(6)
        pytest.fracture_net.activate_nodes()

    def test_activate_fractures(self):
        pytest.fracture_net.activate_fractures([2])
        assert pytest.fracture_net.is_set_active(2)
        assert not pytest.fracture_net.is_set_active(1)
        pytest.fracture_net.activate_fractures()

    def test_deactivate_fractures(self):
        pytest.fracture_net.deactivate_fractures([2])
        assert not pytest.fracture_net.is_set_active(2)
        assert pytest.fracture_net.is_set_active(1)
        pytest.fracture_net.activate_fractures()

    def test_activate_boundary(self):
        pytest.fracture_net.activate_boundaries([1])
        assert pytest.fracture_net.is_group_active(1)
        pytest.fracture_net.activate_boundaries()

    def test_deactivate_boundary(self):
        pytest.fracture_net.deactivate_boundaries([1])
        assert not pytest.fracture_net.is_group_active(1)
        pytest.fracture_net.activate_boundaries()

    def test_fracture_network_to_components_df(self):
        pytest.fracture_net.deactivate_boundaries()

        assert 'boundary' not in pytest.fracture_net.fracture_network_to_components_df()['type']
        pytest.fracture_net.activate_boundaries()
        pytest.fracture_net.deactivate_fractures()
        assert 'fracture' not in pytest.fracture_net.fracture_network_to_components_df()['type']
        pytest.fracture_net.activate_fractures()
        pytest.fracture_net.deactivate_nodes()
        assert 'node' not in pytest.fracture_net.fracture_network_to_components_df()['type']
        pytest.fracture_net.activate_nodes()

    def test_vtk_object(self):
        assert isinstance(pytest.fracture_net.vtk_object(), pyvista.PolyData)
        vtk_obj = pytest.fracture_net.vtk_object()
        assert 'type' in vtk_obj.array_names
        assert 'node' in vtk_obj['type']
        assert isinstance(pytest.fracture_net.vtk_object(include_nodes=False), pyvista.PolyData)
        vtk_obj = pytest.fracture_net.vtk_object(include_nodes=False)
        assert 'type' in vtk_obj.array_names
        assert 'node' not in vtk_obj['type']

    def test_network_object(self):
        assert isinstance(pytest.fracture_net.network_object, networkx.Graph)

    def test_save_csv(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_frac_net_csv.csv')
        pytest.fracture_net.save_csv(file_path)
        assert os.path.isfile(file_path)
        os.remove(file_path)

    def test_save_shp(self):
        cwd = os.getcwd()
        file_path = os.path.join(cwd, 'test_frac_net_shp.shp')
        pytest.fracture_net.save_shp(file_path)
        assert os.path.isfile('nodes_test_frac_net_shp.shp')
        assert os.path.isfile('fractures_test_frac_net_shp.shp')
        assert os.path.isfile('boundaries_test_frac_net_shp.shp')

        paths = glob.glob(os.path.join(cwd, '*_test_frac_net_shp.*'))
        for path in paths:
            os.remove(path)

    def test_crs(self):
        assert pytest.fracture_net.crs is not None
