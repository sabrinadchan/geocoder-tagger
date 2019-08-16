# chicago-elections-scraper
Set of Python 2 functions to [geocode](https://en.wikipedia.org/wiki/Geocoding) well-formated addresses in a pandas `DataFrame` using the [Google Geocoding API](https://developers.google.com/maps/documentation/geocoding/start) and to join resulting coordinates with the features of another set of geospatial data.

## Requirements
* Python 2.7
* GeoPandas - Read the [installation instructions](http://geopandas.org/install.html).
* pandas >= 0.23.4 - See above instructions
* shapely - See above instructions
* Google GeoCoding [API Key](https://developers.google.com/maps/documentation/geocoding/get-api-key)

## Example Use
Suppose you have a CSV file containing information on all of the taquerías in the City of Chicago that includes a field with the taquería's address, and you want to know the number of taquerías in each ward of the city. Maybe you eventually want to create a [choropleth](https://en.wikipedia.org/wiki/Choropleth_map) of the data. The example below walks you through how to use the functions in geocode.py to answer this question.
```python
import geocode
import pandas as pd
import geopandas as gpd
# Be sure to paste your API key into geocode.py or update geocode.API_KEY now.
# e.g. geocode.API_KEY = "YOUR API KEY"

# Read the taqueria data into a DataFrame.
tacos = pd.read_csv("taquerias.csv")

# Process and clean the data as necessary before continuing.
# geocode.preprocess creates columns: 'geocode_error', 'lat', 'lon'.
# Warning: if the columns already exist, they will be overwritten with an empty string.
geocode.preprocess(tacos)

# geocode.geocode_df geocodes addresses in given DataFrame and column one row at a time.
# If the API cannot geocode an address, sets value in 'geocode_error' to True.
geocode.geocode_df(tacos, "address")

# Load DataFrame into GeoPandas GeoDataFrame.
# This step is necessary to perform a spatial join.
tacos_gdf = geocode.build_gdf(tacos)

# Join the coordinates with desired target feature.
# e.g. the Chicago ward boundaries here (download as GeoJSON or Shapefile):
# https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Wards-2015-/sp34-6z76
# The feature_name argument of geocode.tag corresponds to 
# the property element containing the name of the feature.
# In the case of the Chicago wards GeoJSON
# the desired property is "ward" and has a value 1 to 50.
# The new_feature_name argument is optional.
geocode.tag(tacos_gdf, "wards.geojson", "ward")

# Count the number of taquerias in each ward!
tacos_gdf.groupby("ward").count()
```
