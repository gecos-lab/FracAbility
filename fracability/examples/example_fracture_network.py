import pandas as pd
import geopandas as gpd
import inspect
from fracability import DATADIR


def fracture_net_components():

    data = pd.read_csv(f'{DATADIR}/example_fracture_network_data/network_example_data.csv')
    gdf = gpd.GeoDataFrame(data, geometry=gpd.GeoSeries.from_wkt(data["geometry"]))

    return gdf
