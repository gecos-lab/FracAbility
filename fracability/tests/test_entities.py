import networkx
import pytest
import geopandas as gpd
import pyvista

from fracability.Entities import Nodes, Fractures, Boundary, FractureNetwork
from fracability.examples import example_fracture_network


class TestNodes:
    """
    Class used to test Node entity creation
    """

    def test_creation(self):
        data = example_fracture_network.fracture_net_components()
        pytest.nodes_data = data.loc[data['type'] == 'node']

        assert isinstance(Nodes(pytest.nodes_data), Nodes)

        pytest.nodes = Nodes(pytest.nodes_data)

    def test_entity_df(self):
        assert not pytest.nodes.entity_df.empty

    def test_set_entity_df(self):
        pytest.nodes.entity_df = pytest.nodes_data

        assert pytest.nodes.entity_df.equals(pytest.nodes_data)

    def test_vtk_object(self):
        assert isinstance(pytest.nodes.vtk_object, pyvista.PolyData)

        vtk_obj = pytest.nodes.vtk_object
        assert 'type' in vtk_obj.array_names
        assert 'node_type' in vtk_obj.array_names

    def test_network_object(self):
        assert isinstance(pytest.nodes.network_object, networkx.Graph)


class TestFractures:
    """
    Class used to test Fracture entity creation
    """

    def test_creation(self):
        data = example_fracture_network.fracture_net_components()
        pytest.fracture_data = data.loc[data['type'] == 'fracture']

        assert isinstance(Fractures(pytest.fracture_data), Fractures)
        pytest.fractures = Fractures(pytest.fracture_data)

        set_1_data = pytest.fracture_data.loc[pytest.fracture_data['set'] == 1]
        set_2_data = pytest.fracture_data.loc[pytest.fracture_data['set'] == 2]

        assert isinstance(Fractures(set_1_data, 1), Fractures)
        assert isinstance(Fractures(set_2_data, 2), Fractures)
        assert all(Fractures(set_1_data, 1).entity_df['set'] == 1)
        assert all(Fractures(set_2_data, 2).entity_df['set'] == 2)

        pytest.fractures_1 = Fractures(set_1_data, 1)
        pytest.fractures_2 = Fractures(set_2_data, 2)

    def test_entity_df(self):
        assert not pytest.fractures.entity_df.empty

    def test_set_entity_df(self):
        pytest.fractures.entity_df = pytest.fracture_data

        assert pytest.fractures.entity_df.equals(pytest.fracture_data)

    def test_vtk_object(self):
        assert isinstance(pytest.fractures.vtk_object, pyvista.PolyData)

        vtk_obj = pytest.fractures.vtk_object
        assert 'type' in vtk_obj.array_names
        assert 'set' in vtk_obj.array_names
        assert 'RegionId' in vtk_obj.array_names

    def test_network_object(self):
        assert isinstance(pytest.fractures.network_object, networkx.Graph)


class TestBoundary:
    """
    Class used to test Boundary entity creation
    """

    def test_creation(self):
        data = example_fracture_network.fracture_net_components()
        pytest.boundary_data = data.loc[data['type'] == 'boundary']

        assert isinstance(Boundary(pytest.boundary_data), Boundary)

        pytest.boundaries = Boundary(pytest.boundary_data)

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


class TestFractureNetwork:
    """
    Class used to test FractureNetwork entity creation
    """
    def test_add_nodes(self):
        fracture_net = FractureNetwork()
        fracture_net.add_nodes(pytest.nodes)
        assert 1 in set(fracture_net.entity_df.node_type)
        assert 3 in set(fracture_net.entity_df.node_type)
        assert 4 in set(fracture_net.entity_df.node_type)
        assert 5 in set(fracture_net.entity_df.node_type)
        assert 6 in set(fracture_net.entity_df.node_type)

    def test_add_fractures(self):
        fracture_net = FractureNetwork()
        fracture_net.add_fractures(pytest.fractures)
        assert 1 in set(fracture_net.entity_df.fracture_set)
        assert 2 in set(fracture_net.entity_df.fracture_set)

    def test_add_fractures_set(self):
        fracture_net = FractureNetwork()
        fracture_net.add_fractures(pytest.fractures_1)
        fracture_net.add_fractures(pytest.fractures_2)
        assert 1 in set(fracture_net.entity_df.fracture_set)
        assert 2 in set(fracture_net.entity_df.fracture_set)

    # def test_add_boundaries(self):
    #     fracture_net = FractureNetwork()
    #     fracture_net.add_boundaries(pytest.boundaries)
    #     assert 0 in set(fracture_net.entity_df.boundary_group)

    def test_create_fn(self):

        pytest.fracture_net = FractureNetwork()
        pytest.fracture_net.add_nodes(pytest.nodes)
        pytest.fracture_net.add_fractures(pytest.fractures)
        pytest.fracture_net.add_boundaries(pytest.boundaries)

        assert not pytest.fracture_net.entity_df.empty
        assert pytest.fracture_net.fracture_network_to_components_df().equals(example_fracture_network.fracture_net_components())

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

    # def test_network_object(self):
    #     assert isinstance(pytest.entity.network_object, networkx.Graph)