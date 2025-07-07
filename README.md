# Modeling and Predicting NYC (and Surrounding Areas) Transit Demand

## Introduction

This project was created as part of a larger project to devise a plan for much-needed rapid transit (subway/metro) expansion in the NYC metro area. I needed a way to estimate rapid transit ridership at any location within the tri-state area in order to statistically support decisions (such as station locations, route alignments, and proposed service frequencies) within the plan.

I developed a model to do just that, based on realistically available parameters: population density, job density, distance to Midtown Manhattan, the amount of service the station receives or might receive, whether it is a terminus station, whether it's ADA accessible, and whether it's a "commuter" station (a station with a transfer to commuter rail or a bus terminal, for example). In the model, these parameters are represented by `DENSITY_BG`, `JOB_DENSITY_BG_LOG` (log-transformed), `DISTANCE`, `TOTAL_FREQUENCY`, `TERMINUS`, `ADA`, and `COMMUTER`, respectively. There is also an additional variable `FREQUENCY-COMMUTER_INTERACTION` that represents the interaction between `TOTAL_FREQUENCY` and `COMMUTER`.

A number of publically-available resources were used in order to complete this project—these can be found below in the Sources section.

## Results

### Insights

### Model Results
```
                            OLS Regression Results                            
==============================================================================
Dep. Variable:               LOG_2023   R-squared:                       0.702
Model:                            OLS   Adj. R-squared:                  0.696
Method:                 Least Squares   F-statistic:                     120.5
Date:                Fri, 04 Jul 2025   Prob (F-statistic):          1.40e-102
Time:                        22:15:51   Log-Likelihood:                -332.32
No. Observations:                 418   AIC:                             682.6
Df Residuals:                     409   BIC:                             719.0
Df Model:                           8                                         
Covariance Type:            nonrobust                                         
==================================================================================================
                                     coef    std err          t      P>|t|      [0.025      0.975]
--------------------------------------------------------------------------------------------------
const                             11.8028      0.294     40.133      0.000      11.225      12.381
JOB_DENSITY_BG_LOG                 0.0994      0.020      5.065      0.000       0.061       0.138
DISTANCE                          -6.8614      0.639    -10.730      0.000      -8.118      -5.604
TERMINUS                           0.4546      0.132      3.434      0.001       0.194       0.715
TOTAL_FREQUENCY                    0.7942      0.071     11.136      0.000       0.654       0.934
ADA                                0.2581      0.059      4.347      0.000       0.141       0.375
COMMUTER                           3.3727      1.075      3.139      0.002       1.260       5.485
FREQUENCY-COMMUTER_INTERACTION    -0.6323      0.297     -2.128      0.034      -1.216      -0.048
DENSITY_BG                         0.0840      0.027      3.100      0.002       0.031       0.137
==============================================================================
Omnibus:                       13.631   Durbin-Watson:                   1.881
Prob(Omnibus):                  0.001   Jarque-Bera (JB):               17.024
Skew:                          -0.318   Prob(JB):                     0.000201
Kurtosis:                       3.757   Cond. No.                         492.
==============================================================================
```

### Plots
![](plots/linear_plot.png)
![](plots/log_plot.png)

## Instructions
1. Run `datacleaning.py`.
2. To run the model and view the model summary, run `regression.py`.
3. To run the model and generate plots, run `plot.py`. You must run
`regression.py` first in order to generate the plots.
4. To predict ridership at given stations/locations, run `predict.py`.
A sample dataset of stations/locations is provided in `sample.csv`, which is
the data `predict.py` uses. Modify this table to predict ridership for
stations/locations of your own choosing. To do so, you must include a name
for the station, its latitude and longitude coordinates, the lines that serve
the station, whether it's a terminus station, whether it's a commuter station,
and whether it's a transfer station. You can also edit `sample_frequencies.csv`
to include custom frequency data for any additional lines you include. However,
this isn't mandatory, and a default value of 10 trains per hour will be
assigned if you choose to add a new line. A new table with the predicted
ridership will be saved to `calculated_ridership.csv`.

## Documentation and Notes
`JOB_DENSITY_BG_LOG`: Log-transformed in order to counteract the effect of heavily-skewed job density geographic data.

`TOTAL_FREQUENCY`: Combines average weekday TPH values (sourced from [NYC Subway Frequencies (Gregory Feliu)](https://github.com/gregfeliu/NYC-Subway-Frequencies)) for each service that serves a station.

`COMMUTER`: Possible values are 0 (not a commuter station), 0.5 (minor commuter station), and 1.0 (major commuter station). The reason for the distinction between minor and major is that a station like Atlantic Av-Barclays Center, while still a commuter hub, is nowhere near as significant as Grand Central-42 St and should be reflected as such in the data. Additionally, I assigned the value 0.5 to each 34 St-Penn Station because the commuter hub effect from Penn Station is split between the station on the Broadway–Seventh Avenue Line and the station on the Eighth Avenue Line. For additional stations of your choosing that you'd like to predict, the value for `COMMUTER` can be assigned at your discretion.

`FREQUENCY-COMMUTER_INTERACTION`: I found that the model was overestimating ridership at major commuter hubs, so I introduced an interaction between `TOTAL_FREQUENCY` and `COMMUTER` to counteract this.

## Sources
1. [MTA 2023 Subway Ridership Data](https://www.mta.info/agency/new-york-city-transit/subway-bus-ridership-2023)
2. [MTA Subway Stations (NY Open Data)](https://data.ny.gov/Transportation/MTA-Subway-Stations/39hk-dx4f/data_preview)
3. [American Community Survey 5-Year Data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
4. [LEHD Origin-Destination Employment Statistics (LODES) Workplace Area Characteristics (WAC) Data](https://lehd.ces.census.gov/data/)
5. [NYC Subway Frequencies (Gregory Feliu)](https://github.com/gregfeliu/NYC-Subway-Frequencies)
