import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm

df = pd.read_csv("csv_database/df.csv")

# Fit model
X = df[
    ["JOB_DENSITY_BG_LOG", "DISTANCE", "TERMINUS", "TOTAL_FREQUENCY", "ADA",
     "COMMUTER", "FREQUENCY-COMMUTER_INTERACTION", "DENSITY_BG"]
    ]
X = sm.add_constant(X)
y = df["LOG_2023"]
model = sm.OLS(y, X).fit()

# Add columns for predicted vs. actual values
df["ACTUAL"] = np.expm1(df["LOG_2023"])
df["PREDICTED"] = np.expm1(model.predict(X))

# Linear plot
plt.figure(figsize=(10, 7))
sns.set(style="whitegrid")
sns.scatterplot(df, x = "ACTUAL", y = "PREDICTED")
sns.regplot(df, x = "ACTUAL", y = "PREDICTED", scatter = False)
tick_vals = list(range(0, 60_000_001, 5_000_000))
tick_labels = [f"{x//1_000_000}M" for x in tick_vals]
plt.xticks(tick_vals, tick_labels)
plt.yticks(tick_vals, tick_labels)
plt.xlabel("Actual Ridership (millions/year)")
plt.ylabel("Predicted Ridership (millions/year)")
plt.title("Predicted vs. Actual Ridership (2023, linear scale)")
plt.grid(True, which = "both", linestyle= "--")
plt.tight_layout()
plt.savefig("plots/linear_plot.png")

# Log plot
plt.figure(figsize=(10, 7))
sns.set(style="whitegrid")
sns.scatterplot(df, x = "ACTUAL", y = "PREDICTED")
sns.regplot(df, x = "ACTUAL", y = "PREDICTED", scatter = False)
plt.xscale("log")
plt.yscale("log")
ticks = [1e4, 1e5, 1e6, 1e7, 6e7]
labels = ["10K", "100K", "1M", "10M", "60M"]
plt.xticks(ticks, labels)
plt.yticks(ticks, labels)
plt.xlabel("Actual Ridership")
plt.ylabel("Predicted Ridership")
plt.title("Predicted vs. Actual Ridership (2023, log scale)")
plt.grid(True, which = "both", linestyle= "--")
plt.tight_layout()
plt.savefig("plots/log_plot.png")
