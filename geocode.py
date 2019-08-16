import pandas as pd
import requests
import json
import geopandas as gpd
from shapely.geometry import Point

# paste your API key
API_KEY = ""
URL = "https://maps.googleapis.com/maps/api/geocode/json"

def preprocess_df(df): 
  for column in ['geocode_error', 'lat', 'lon']:
    df[column] = ""  

def build_payload(address):
  return {
    'address': address,
    'key': API_KEY
}

def geocode_df(df, address_col):
  for i in df.index:
    payload = build_payload(df.at[i, address_col])
    r = requests.get(URL, params=payload)
    json_response = r.json()

    if json_response['status'] != "OK":
      df.at[i, 'lat'] = 0
      df.at[i, 'lon'] = 0
      df.at[i, 'geocode_error'] = True
      print "ERROR at {}: {} for address {}".format(i, json_response['status'], df.at[i, address_col])
    else:
      json_results = json_response['results'][0]
      lat, lon = json_results['geometry']['location'].values()
      df.at[i, 'lat'] = lat
      df.at[i, 'lon'] = lon
      df['geocode_error'] = False

# If API cannot geocode an address(es) for whatever reason (typo, poor formatting)
# run geocode_errors after editing the addresses manually with pandas to try geocoding
# the records again without having to re-process successfully geocoded data.
def geocode_errors(df, address_col):
  geocode_df(df[df.geocode_error], address_col)

def build_gdf(df):
  gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.lon, df.lat)])
  gdf.crs = {'init': 'epsg:4326'}
  return gdf

def tag(gdf, file, feature_name, new_feature_name=None):  
  boundary = gpd.read_file(file).to_crs({'init': 'epsg:4326'})
  intersection = gpd.sjoin(gdf, boundary[[feature_name, 'geometry']], how='left', op='intersects')
  intersection[feature_name] = intersection[feature_name].fillna('')
  if new_feature_name:
    intersection.rename(columns={feature_name: new_feature_name}, inplace=True)
  intersection.drop('index_right', axis=1, inplace=True)
  return intersection
