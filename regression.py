import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
from shapely import distance
from shapely import wkt
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

# Import datasets
data = pd.read_csv("csv_database/data.csv")
merge = pd.read_csv("csv_database/merge.csv")
merge_t = pd.read_csv("csv_database/merge_t.csv")
jobs = pd.read_csv("csv_database/jobs.csv")
jobs_t = pd.read_csv("csv_database/jobs_t.csv")
frequencies = pd.read_csv("frequencies.csv")

# Merge ridership dataset with block group dataset
df = data.join(
    merge.set_index("BLOCK GROUP"),
    on = "BLOCK GROUP",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {
    "POPULATION": "POPULATION_BG",
    "AREA": "AREA_BG",
    "DENSITY": "DENSITY_BG",
    "INCOME": "INCOME_BG"})

# Merge ridership dataset with tract dataset
df = df.join(
    merge_t.set_index("TRACT"),
    on = "TRACT",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(
    columns = {"POPULATION": "POPULATION_TR",
               "AREA": "AREA_TR",
               "DENSITY": "DENSITY_TR",
               "INCOME":"INCOME_TR",
               "POVERTY_RATE":"POVERTY_TR"})

# Merge job dataset with block group dataset
df = df.join(
    jobs.set_index("BLOCK GROUP"),
    on = "BLOCK GROUP",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {"JOBS": "JOBS_BG"})
df["B_JOB_DENSITY"] = df["JOBS_BG"] / df["AREA_BG"]

# Merge job dataset with tract dataset
df = df.join(
    jobs_t.set_index("TRACT"),
    on = "TRACT",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {"JOBS": "JOBS_TR"})
df["JOB_DENSITY_TR"] = df["JOBS_TR"] / df["AREA_TR"]

# Create frequency dataset
frequencies = frequencies[frequencies["Day of Week"] == "Weekday"]
frequencies = frequencies.drop(columns = ["Avg. Wait"])
frequencies["TPH"] = frequencies["TPH"].astype(int)

# Data cleaning
df = df.drop_duplicates(subset=["Station"])
df["2019"] = df["2019"].str.replace(",", "").astype(float)
df["2023"] = df["2023"].str.replace(",", "").astype(float)

# Log of ridership
df["LOG_2019"] = np.log1p(df["2019"])
df["LOG_2023"] = np.log1p(df["2023"])

# Log of job density
df["JOB_DENSITY_BG_LOG"] = np.log1p(df["B_JOB_DENSITY"])
df["JOB_DENSITY_TR_LOG"] = np.log1p(df["JOB_DENSITY_TR"])

# Standardize population density
df["DENSITY_BG"] = StandardScaler().fit_transform(df[["DENSITY_BG"]])
df["DENSITY_TR"] = StandardScaler().fit_transform(df[["DENSITY_TR"]])

# Define transfer stations
df["TRANSFER"] = (df["id"] > 600) | (df["id"].isin(
    [461, 279, 167, 42])) 
df["TRANSFER"] = df["TRANSFER"].astype(int)

# Define terminus stations
df["TERMINUS"] = df["id"].isin(
    [1, 39, 58, 108, 138, 143, 195, 209, 203, 210, 254,
     278, 293, 359, 360, 378, 416, 442, 447, 471])
df["TERMINUS"] = df["TERMINUS"].astype(int)

# Define commuter stations
df["COMMUTER"] = 0.0
df.loc[df["id"].isin([610, 279, 447, 611]), "COMMUTER"] = 1.0
df.loc[df["id"].isin([318, 164, 617, 607]), "COMMUTER"] = 0.5

# Convert ADA column to integer
df["ADA"] = df["ADA"].astype(int)

# Create "LINES" and "TOTAL_FREQUENCY" columns
df["LINES"] = ""
df["TOTAL_FREQUENCY"] = 0

def extract_lines(station):
    line_groups = re.findall(r"\((.*?)\)", station)
    lines = [line.strip() for group in line_groups for line in group.split(",")]
    return lines

# Iterate through dataset to extract lines and calculate frequency
for i, row in df.iterrows():
    routes = extract_lines(row["Station"])
    df.at[i, "LINES"] = routes
    total_freq = 0
    for j in routes:
        for k, row_k in frequencies.iterrows():
            if row_k["Service"] == j:
                total_freq = total_freq + row_k["TPH"]
    df.at[i, "TOTAL_FREQUENCY"] = total_freq

# Log of total frequency
df["TOTAL_FREQUENCY"] = np.log1p(df["TOTAL_FREQUENCY"])

# Interaction between commuter and total frequency variables
df["FREQUENCY-COMMUTER_INTERACTION"] = df["TOTAL_FREQUENCY"] * df["COMMUTER"]

# Final data cleaning and export to CSV
df = df[
    ["2019", "2023", "LOG_2019", "LOG_2023", "id", "Station",
     "Stop Name", "JOB_DENSITY_BG_LOG", "JOB_DENSITY_TR_LOG", "DENSITY_BG",
     "DENSITY_TR", "DISTANCE", "TERMINUS", "TOTAL_FREQUENCY", "ADA",
     "COMMUTER", "TRANSFER", "FREQUENCY-COMMUTER_INTERACTION",]
    ]
df = df.dropna()
df.to_csv("csv_database/df.csv")

# Fit model
X = df[
    ["JOB_DENSITY_BG_LOG", "DISTANCE", "TERMINUS", "TOTAL_FREQUENCY", "ADA",
     "COMMUTER", "FREQUENCY-COMMUTER_INTERACTION", "DENSITY_BG"]
    ]
X = sm.add_constant(X)
y = df["LOG_2023"]
model = sm.OLS(y, X).fit()
print(model.summary())
