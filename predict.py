import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import distance
from shapely import wkt
from shapely.geometry import Point
from sklearn.preprocessing import StandardScaler

# Import datasets
data = pd.read_csv("csv_database/data.csv")
merge = pd.read_csv("csv_database/merge.csv")
merge_t = pd.read_csv("csv_database/merge_t.csv")
jobs = pd.read_csv("csv_database/jobs.csv")
jobs_t = pd.read_csv("csv_database/jobs_t.csv")
frequencies = pd.read_csv("frequencies.csv")
merge["geometry"] = merge["geometry"].apply(wkt.loads)
merge = gpd.GeoDataFrame(merge, geometry="geometry")

# Standardize population density
merge["DENSITY"] = StandardScaler().fit_transform(merge[["DENSITY"]])

# Function to predict ridership for a point with given parameters
def predict_ridership(latitude, longitude, frequency, terminus,
                      commuter, transfer):
    coord = Point(longitude, latitude) # Create shapely Point

    # Find if Point is within a block group in the dataset
    for i, row in merge.iterrows():
        polygon = row["geometry"]
        if polygon.contains(coord):
            index_id = i
            geo_id = row["BLOCK GROUP"]
            geo_id_t = row["GEOID_T"]
            break

    # Data preparation
    P_B_JOB_DENSITY = jobs.loc[
        jobs[
            "BLOCK GROUP"] == geo_id,
        "JOBS"].values[0] / merge.at[index_id, "AREA"]
    P_B_DENSITY = merge.at[index_id, "DENSITY"]
    P_DISTANCE = distance(coord, Point((-73.9840, 40.7549)))
    LOG_FREQ_X_COMMUTER = np.log1p(frequency) * commuter

    # Equation
    log_pred = (
            11.7557
            + 0.1002 * np.log1p(P_B_JOB_DENSITY)
            - 6.8646 * np.log1p(P_DISTANCE)
            + 0.4503 * terminus
            + 0.8109 * np.log1p(frequency)
            + 0.2575 * 1
            + 4.2903 * commuter
            - 0.9410 * LOG_FREQ_X_COMMUTER
            + 0.0818 * P_B_DENSITY
        )
    return np.exp(log_pred)

# Function to predict ridership for multiple given stations
def predict_ridership_for_data_frame(test_data, freq):
    given_data = pd.read_csv(test_data)
    results = pd.DataFrame({"Station": [], "Ridership": []})
    for i, row in given_data.iterrows():
        print("-", sep=" ", end="", flush=True)
        routes = row["Lines"].split(",")
        given_data.at[i, "Lines"] = routes
        total_freq = 0
        for j in routes:
            for k, row_k in freq.iterrows():
                if row_k["Service"] == j:
                    total_freq = total_freq + row_k["TPH"]
                given_data.at[i, "Frequency"] = total_freq
        results = pd.concat(
                [results,
                 pd.DataFrame(
                     {"Station": [row["Stop Name"]],
                      "Ridership": [predict_ridership
                      (row["Latitude"], row["Longitude"],
                       total_freq, row["Terminus"],
                       row["Commuter"], row["Transfer"])]
                      })], ignore_index = True)
    print("\nFinished")
    return results

# Predict ridership for stations in "sample.csv"
save_ridership = predict_ridership_for_data_frame(
    "test_data/sample.csv", frequencies)

# Export calculated ridership to CSV
save_ridership.to_csv("test_data/calculated_ridership.csv")
