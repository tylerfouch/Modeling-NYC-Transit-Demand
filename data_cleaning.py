import sqlite3
import pandas as pd
from census import Census
from us import states
import geopandas as gpd
import pygris
from shapely.geometry import Point
from shapely import distance
from shapely.geometry.polygon import Polygon

# Read data from SQLite database
conn = sqlite3.connect("sql_database/database.db")
data = pd.read_sql("SELECT * FROM merged", conn)
ny_jobs = pd.read_sql("SELECT * FROM ny_jobs", conn)
nj_jobs = pd.read_sql("SELECT * FROM nj_jobs", conn)
ct_jobs = pd.read_sql("SELECT * FROM ct_jobs", conn)

# Access Census data with API key
api_key = "c1d0cc448c6472e0f768a7f9897215247d35d688"
c = Census(api_key)

# Get population datasets for block groups
ny_pop = c.acs5.state_county_blockgroup(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.NY.fips, Census.ALL, Census.ALL)
nj_pop = c.acs5.state_county_blockgroup(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.NJ.fips, Census.ALL, Census.ALL)
ct_pop = c.acs5.state_county_blockgroup(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.CT.fips, Census.ALL, Census.ALL)

# Get population datasets for tracts
ny_pop_t = c.acs5.state_county_tract(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.NY.fips, Census.ALL, Census.ALL)
nj_pop_t = c.acs5.state_county_tract(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.NJ.fips, Census.ALL, Census.ALL)
ct_pop_t = c.acs5.state_county_tract(
    ("NAME", "B01003_001E", "B19013_001E"),
    states.CT.fips, Census.ALL, Census.ALL)

# Convert Census datasets from lists to dataframes
ny_pop = pd.DataFrame(ny_pop[1:], columns = ny_pop[0])
nj_pop = pd.DataFrame(nj_pop[1:], columns = nj_pop[0])
ct_pop = pd.DataFrame(ct_pop[1:], columns = ct_pop[0])
ny_pop_t = pd.DataFrame(ny_pop_t[1:], columns = ny_pop_t[0])
nj_pop_t = pd.DataFrame(nj_pop_t[1:], columns = nj_pop_t[0])
ct_pop_t = pd.DataFrame(ct_pop_t[1:], columns = ct_pop_t[0])

# Create ID columns
ny_pop["GEOID"] = (ny_pop["state"] + ny_pop["county"] +
                   ny_pop["tract"] + ny_pop["block group"])
nj_pop["GEOID"] = (nj_pop["state"] + nj_pop["county"]
                   + nj_pop["tract"] + nj_pop["block group"])
ct_pop["GEOID"] = (ct_pop["state"] + ct_pop["county"]
                   + ct_pop["tract"] + ct_pop["block group"])
ny_pop["GEOID_T"] = ny_pop["state"] + ny_pop["county"] + ny_pop["tract"]
nj_pop["GEOID_T"] = nj_pop["state"] + nj_pop["county"] + nj_pop["tract"]
ct_pop["GEOID_T"] = ct_pop["state"] + ct_pop["county"] + ct_pop["tract"]
ny_pop_t["GEOID"] = ny_pop_t["state"] + ny_pop_t["county"] + ny_pop_t["tract"]
nj_pop_t["GEOID"] = nj_pop_t["state"] + nj_pop_t["county"] + nj_pop_t["tract"]
ct_pop_t["GEOID"] = ct_pop_t["state"] + ct_pop_t["county"] + ct_pop_t["tract"]
ny_jobs["BLOCK GROUP"] = ny_jobs["w_geocode"].astype(str).str[:12]
nj_jobs["BLOCK GROUP"] = nj_jobs["w_geocode"].astype(str).str[:12]
ct_jobs["BLOCK GROUP"] = ct_jobs["w_geocode"].astype(str).str[:12]
ny_jobs["TRACT"] = ny_jobs["w_geocode"].astype(str).str[:11]
nj_jobs["TRACT"] = nj_jobs["w_geocode"].astype(str).str[:11]
ct_jobs["TRACT"] = ct_jobs["w_geocode"].astype(str).str[:11]

# Sum columns (different categories of jobs) in job datasets
ny_jobs["JOBS"] = ny_jobs.iloc[:, 1:51].sum(axis=1, numeric_only=True)
ny_jobs = ny_jobs[["w_geocode", "BLOCK GROUP", "TRACT", "JOBS"]]
nj_jobs["JOBS"] = nj_jobs.iloc[:, 1:50].sum(axis=1, numeric_only=True)
nj_jobs = nj_jobs[["w_geocode", "BLOCK GROUP", "TRACT", "JOBS"]]
ct_jobs["JOBS"] = ct_jobs.iloc[:, 1:50].sum(axis=1, numeric_only=True)
ct_jobs = ct_jobs[["w_geocode", "BLOCK GROUP", "TRACT", "JOBS"]]

# Combine population datasets for NY, NJ, and CT, and export to CSV
pop = pd.concat([ny_pop, nj_pop, ct_pop], ignore_index=True)
pop_t = pd.concat([ny_pop_t, nj_pop_t, ct_pop_t], ignore_index=True)
pop.to_csv("csv_database/pop.csv")
pop_t.to_csv("csv_database/pop_t.csv")

# Combine job datasets (by block group) for NY, NJ, and CT, and export to CSV
jobs = pd.concat([ny_jobs, nj_jobs, ct_jobs], ignore_index=True)
jobs = jobs.groupby(["BLOCK GROUP"])["JOBS"].sum()
jobs.to_csv("csv_database/jobs.csv")

# Combine job datasets (by tract) for NY, NJ, and CT, and export to CSV
jobs_t = pd.concat([ny_jobs, nj_jobs, ct_jobs], ignore_index=True)
jobs_t = jobs_t.groupby(["TRACT"])["JOBS"].sum()
jobs_t.to_csv("csv_database/jobs_t.csv")

# Get geographic datasets for block groups
ny_geo = pygris.block_groups(state = "NY", cb = True, cache = True)
nj_geo = pygris.block_groups(state = "NJ", cb = True, cache = True)
ct_geo = pygris.block_groups(state = "CT", cb = True, cache = True)

# Get geographic datasets for tracts
ny_geo_t = pygris.tracts(state = "NY", cb = True, cache = True)
nj_geo_t = pygris.tracts(state = "NJ", cb = True, cache = True)
ct_geo_t = pygris.tracts(state = "CT", cb = True, cache = True)

# Combine geographic datasets for NY, NJ, and CT, and export to CSV
geo = pd.concat([ny_geo, nj_geo, ct_geo], ignore_index=True)
geo_t = pd.concat([ny_geo_t, nj_geo_t, ct_geo_t], ignore_index=True)
geo.to_csv("csv_database/geo.csv")
geo_t.to_csv("csv_database/geo_t.csv")

# Merge population and geo datasets
merge = geo.join(
    pop.set_index("GEOID"),
    on = "GEOID",
    lsuffix = "_left",
    rsuffix = "_right")
merge_t = geo_t.join(
    pop_t.set_index("GEOID"),
    on = "GEOID",
    lsuffix = "_left",
    rsuffix = "_right")

# Calculate block group population density
merge = merge.to_crs(epsg=3857)
sindex = merge.sindex
merge["AREA"] = merge.geometry.area / 2.59e+6
merge["DENSITY"] = merge["B01003_001E"] / merge["AREA"]

# Calculate tract population density
merge_t = merge_t.to_crs(epsg=3857)
sindex = merge_t.sindex
merge_t["AREA"] = merge_t.geometry.area / 2.59e+6
merge_t["DENSITY"] = merge_t["B01003_001E"] / merge_t["AREA"]

# Clean up columns
merge = merge.drop(
    columns=["STATEFP", "COUNTYFP", "TRACTCE",
             "BLKGRPCE", "GEOIDFQ", "NAME_left",
             "NAMELSAD", "LSAD", "ALAND", "AWATER",
             "NAME_right", "state", "county",
             "tract", "block group"])
merge = merge.rename(
    columns={"B01003_001E": "POPULATION",
             "GEOID": "BLOCK GROUP",
             "B19013_001E": "INCOME"})
merge_t = merge_t.drop(
    columns=["STATEFP", "COUNTYFP", "TRACTCE",
             "GEOIDFQ", "NAME_left", "NAMELSAD",
             "LSAD", "ALAND", "AWATER",
             "NAME_right", "state", "county",
             "tract"])
merge_t = merge_t.rename(
    columns={"B01003_001E": "POPULATION",
             "GEOID": "TRACT",
             "B19013_001E": "INCOME"})

# Change projection to 4326
merge = merge.to_crs(4326)
merge_t = merge_t.to_crs(4326)

# Export merged (population and geo data) block group and tract datasets to CSV
merge.to_csv("csv_database/merge.csv")
merge_t.to_csv("csv_database/merge_t.csv")

# Add columns to ridership dataset for geopandas points, block groups, and tracts
data["POINT"] = gpd.points_from_xy(x = data["Long"], y = data["Lat"], crs = 4326) 
data["BLOCK GROUP"] = ""
data["TRACT"] = ""
for i, row in data.iterrows():
    point = row["POINT"]
    for j, poly_row in merge.iterrows():
        polygon = poly_row["geometry"]
        if polygon.contains(point):
            data.at[i, "BLOCK GROUP"] = poly_row["BLOCK GROUP"]
            data.at[i, "TRACT"] = poly_row["GEOID_T"]
            print("-", sep=" ", end="", flush=True)
            break

# Add column for each point's distance to midtown
data["DISTANCE"] = distance(data["POINT"], Point((-73.9840, 40.7549)))

print("Finished")

# Export final data to CSV
data.to_csv("csv_database/data.csv")
