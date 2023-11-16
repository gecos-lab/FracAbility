from fracability.examples import example_fracture_network
import pytest
from fracability import Entities
from fracability.operations.Geometry import tidy_intersections

@pytest.fixture(scope="session", autouse=True)
def environment_var():
    pytest.shp_path, _ = example_fracture_network.fracture_net_subset()


def test_nodes_conn():
    set_1 = Entities.Fractures(shp=pytest.shp_path['set_1'], set_n=1)
    set_2 = Entities.Fractures(shp=pytest.shp_path['set_2'], set_n=2)

    bounds = Entities.Boundary(shp=pytest.shp_path['bounds'])

    frac_net = Entities.FractureNetwork()
    frac_net.add_fractures(set_1)
    frac_net.add_fractures(set_2)
    frac_net.add_boundaries(bounds)

    tidy_intersections(frac_net)

    nodes_conn(frac_net)
    control_topology = example_fracture_network.fracture_net_control_topology()['complete']

    print(control_topology)
    print(frac_net.nodes.entity_df)

    assert not frac_net.nodes.entity_df.empty
    assert frac_net.nodes.entity_df.equals(control_topology)
