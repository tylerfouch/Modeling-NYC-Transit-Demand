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
frequencies = pd.read_csv("csv_database/frequencies.csv")

# Merge ridership dataset with block group dataset
df = data.join(
    merge.set_index("BLOCK GROUP"),
    on = "BLOCK GROUP",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {
    "POPULATION": "B_POP",
    "AREA": "B_AREA",
    "DENSITY": "B_DENSITY",
    "INCOME": "B_INCOME"})

# Merge ridership dataset with tract dataset
df = df.join(
    merge_t.set_index("TRACT"),
    on = "TRACT",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(
    columns = {"POPULATION": "T_POP",
               "AREA": "T_AREA",
               "DENSITY": "T_DENSITY",
               "INCOME":"T_INCOME",
               "POVERTY_RATE":"T_POVERTY_RATE"})

# Merge job dataset with block group dataset
df = df.join(
    jobs.set_index("BLOCK GROUP"),
    on = "BLOCK GROUP",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {"JOBS": "B_JOBS"})
df["B_JOB_DENSITY"] = df["B_JOBS"] / df["B_AREA"]
df["B_COMB_DENSITY"] = df["B_JOB_DENSITY"] + df["B_DENSITY"]

# Merge job dataset with tract dataset
df = df.join(
    jobs_t.set_index("TRACT"),
    on = "TRACT",
    lsuffix = "_left",
    rsuffix = "_right")
df = df.rename(columns = {"JOBS": "T_JOBS"})
df["T_JOB_DENSITY"] = df["T_JOBS"] / df["T_AREA"]
df["T_COMB_DENSITY"] = df["T_JOB_DENSITY"] + df["T_DENSITY"]

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

# Log of population and job density
df["LOG_B_DENSITY"] = np.log1p(df["B_DENSITY"])
df["LOG_B_JOB_DENSITY"] = np.log1p(df["B_JOB_DENSITY"])
df["LOG_T_DENSITY"] = np.log1p(df["T_DENSITY"])
df["LOG_T_JOB_DENSITY"] = np.log1p(df["T_JOB_DENSITY"])

# Standardize population density
df["B_DENSITY"] = StandardScaler().fit_transform(df[["B_DENSITY"]])
df["T_DENSITY"] = StandardScaler().fit_transform(df[["T_DENSITY"]])

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

# Create "LINES" and "TOTAL_FREQ" columns
df["LINES"] = ""
df["TOTAL_FREQ"] = 0

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
    df.at[i, "TOTAL_FREQ"] = total_freq

# Log of total frequency
df["TOTAL_FREQ"] = np.log1p(df["TOTAL_FREQ"])

# Interaction between commuter and total frequency variables
df["FREQ_X_COMMUTER"] = df["TOTAL_FREQ"] * df["COMMUTER"]

# Final data cleaning and export to CSV
df = df[
    ["2019", "2023", "LOG_2019", "LOG_2023", "id", "Station",
     "Stop Name", "LOG_B_JOB_DENSITY", "LOG_T_JOB_DENSITY", "B_DENSITY",
     "T_DENSITY", "DISTANCE", "TERMINUS", "TOTAL_FREQ", "ADA",
     "COMMUTER", "TRANSFER", "FREQ_X_COMMUTER",]
    ]
df = df.dropna()
df.to_csv("csv_database/df.csv")

# Fit model
X = df[
    ["LOG_B_JOB_DENSITY", "DISTANCE", "TERMINUS", "TOTAL_FREQ", "ADA",
     "COMMUTER", "FREQ_X_COMMUTER", "B_DENSITY"]
    ]
X = sm.add_constant(X)
y = df["LOG_2023"]
model = sm.OLS(y, X).fit()
print(model.summary())
