import pandas as pd
import geopandas as gpd
from fracability import DATADIR


def fracture_net_components():
    """
    method used to get a complete and correct fracture network csv
    :return: GeoPandas dataframe
    """

    data = pd.read_csv(f'{DATADIR}/example_fracture_network_data/network_example_data.csv')
    gdf = gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data["geometry"]), crs='epsg:32632')

    return gdf


def fracture_net_control_intersection():
    """
    method used to get the csv to control correct intersections
    :return: GeoPandas dataframe
    """
    data = pd.read_csv(f'{DATADIR}/example_fracture_network_data/control_data/subset_network_control_intersection.csv')
    gdf = gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data["geometry"]), crs='epsg:32632')

    data_nb = pd.read_csv(f'{DATADIR}/example_fracture_network_data/control_data/subset_network_control_intersection_no_bounds.csv')
    gdf_nb = gpd.GeoDataFrame(data_nb, geometry=gpd.GeoSeries.from_wkt(data_nb["geometry"]), crs='epsg:32632')

    data_ns1 = pd.read_csv(f'{DATADIR}/example_fracture_network_data/control_data/subset_network_control_intersection_no_s1.csv')
    gdf_ns1 = gpd.GeoDataFrame(data_ns1, geometry=gpd.GeoSeries.from_wkt(data_ns1["geometry"]), crs='epsg:32632')

    return {'complete': gdf, 'nb': gdf_nb, 'ns1':gdf_ns1}


def fracture_net_control_topology():
    """
    method used to get the csv to control correct intersections
    :return: GeoPandas dataframe
    """
    data = pd.read_csv(f'{DATADIR}/example_fracture_network_data/control_data/subset_network_control_topology.csv')
    gdf = gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data["geometry"]), crs='epsg:32632')

    return {'complete': gdf}


def fracture_net_subset() -> tuple[dict, dict]:
    """
    Method used to get the directories of shapefiles and the corresponding gdf of a subset of the complete example. It
    returns a tuple of dicts one containing the paths the other the gdf

    :return: tuple of dicts
    """
    n1_path = f'{DATADIR}/example_fracture_network_data/shp/set_1_subset.shp'
    n2_path = f'{DATADIR}/example_fracture_network_data/shp/set_2_subset.shp'

    n_path = f'{DATADIR}/example_fracture_network_data/shp/Fracture_network_subset.shp'
    b_path = f'{DATADIR}/example_fracture_network_data/shp/Interpretation_boundary_laghettoSalza.shp'

    fracs = gpd.read_file(n_path)

    fracs_1 = gpd.read_file(n1_path)
    fracs_2 = gpd.read_file(n2_path)
    bounds_gpd = gpd.read_file(b_path)

    return {'fractures': n_path, 'set_1': n1_path, 'set_2': n2_path, 'bounds': b_path}, \
           {'fractures': fracs, 'set_1': fracs_1, 'set_2': fracs_2, 'bounds': bounds_gpd}


def fracture_net() -> tuple[dict, dict]:
    """
        Method used to get the directories of shapefiles and the corresponding gdf of a complete network example. It
        returns a tuple of dicts one containing the paths the other the gdf

        :return: tuple of dicts
    """
    n1_path = f'{DATADIR}/example_fracture_network_data/shp/Set_1.shp'
    n2_path = f'{DATADIR}/example_fracture_network_data/shp/Set_2.shp'

    n_path = f'{DATADIR}/example_fracture_network_data/shp/Fracture_network.shp'
    b_path = f'{DATADIR}/example_fracture_network_data/shp/Interpretation_boundary_laghettoSalza.shp'

    fracs = gpd.read_file(n_path)

    fracs_1 = gpd.read_file(n1_path)
    fracs_2 = gpd.read_file(n2_path)
    bounds_gpd = gpd.read_file(b_path)

    return {'fractures': n_path, 'set_1': n1_path, 'set_2': n2_path, 'bounds': b_path}, \
        {'fractures': fracs, 'set_1': fracs_1, 'set_2': fracs_2, 'bounds': bounds_gpd}