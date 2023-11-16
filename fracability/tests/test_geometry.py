from fracability.examples import example_fracture_network
import pytest
from fracability import Entities

@pytest.fixture(scope="session", autouse=True)
def environment_var():
    pytest.shp_path, _ = example_fracture_network.fracture_net_subset()


def test_tidy_intersections():

    set_1 = Entities.Fractures(shp=pytest.shp_path['set_1'], set_n=1)
    set_2 = Entities.Fractures(shp=pytest.shp_path['set_2'], set_n=2)

    bounds = Entities.Boundary(shp=pytest.shp_path['bounds'])

    frac_net = Entities.FractureNetwork()
    frac_net.add_fractures(set_1)
    frac_net.add_fractures(set_2)
    frac_net.add_boundaries(bounds)

    control_df = example_fracture_network.fracture_net_control_intersection()

    assert isinstance(tidy_intersections(frac_net, inplace=False), Entities.FractureNetwork)
    assert tidy_intersections(frac_net, inplace=False).fracture_network_to_components_df().equals(control_df['complete'])
    frac_net.deactivate_boundaries()
    assert isinstance(tidy_intersections(frac_net, inplace=False), Entities.FractureNetwork)
    assert tidy_intersections(frac_net, inplace=False).fracture_network_to_components_df().equals(control_df['nb'])
    frac_net.activate_boundaries()
    frac_net.activate_fractures([2])
    assert isinstance(tidy_intersections(frac_net, inplace=False), Entities.FractureNetwork)
    assert tidy_intersections(frac_net, inplace=False).fracture_network_to_components_df().equals(control_df['ns1'])
    frac_net.activate_fractures()


def test_calculate_length():

    set_1 = Entities.Fractures(shp=pytest.shp_path['set_1'], set_n=1)
    set_2 = Entities.Fractures(shp=pytest.shp_path['set_2'], set_n=2)

    bounds = Entities.Boundary(shp=pytest.shp_path['bounds'])

    frac_net = Entities.FractureNetwork()
    frac_net.add_fractures(set_1)
    frac_net.add_fractures(set_2)
    frac_net.add_boundaries(bounds)

    calculate_seg_length(set_1)
    assert 'lengths' in set_1.entity_df.columns
    assert 'length' in set_1.vtk_object.array_names
    calculate_seg_length(frac_net)
    assert 'lengths' in frac_net.fractures.entity_df

