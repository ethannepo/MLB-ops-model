#!/usr/bin/env python
# coding: utf-8

# import files into DataFrames and make one test DataFrame
# 2024 is fully test data

import requests
import datetime
import pandas as pd
from io import StringIO

base_url = ("https://baseballsavant.mlb.com/statcast_search?hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea={year}%7C&hfSit=&player_type=batter&hfOuts=&hfOpponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt=&game_date_lt=&hfMo=&hfTeam=&home_road=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&hfFlag=&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas={min_pas}&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&chk_stats_k_percent=on&chk_stats_bb_percent=on&chk_stats_xba=on&chk_stats_obp=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xwoba=on&chk_stats_swing_miss_percent=on&chk_stats_launch_speed=on&chk_stats_launch_angle=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on#results")

years = [2017, 2018, 2019, 2021, 2022, 2023, 2024, 2025]
dfs = {}

# Create urls for every year
for year in years:
    if year == 2025:
        today = datetime.date.today()
        days_into_season = (today - datetime.date(2025, 3, 27))
        min_pas_2025 = (((3.1*162)/187) * days_into_season).days
        if (min_pas_2025 <= 400):
            url = base_url.format(year = 2025, min_pas = min_pas_2025)
        else:
            url = base_url.format(year = 2025, min_pas = 400)
    else:
        url = base_url.format(year = year, min_pas = 400)

    response = requests.get(url)
    html_string = StringIO(response.text)
    data = pd.read_html(html_string)

    df = pd.DataFrame(data[0])

    df['OPS'] = (df['OBP'] + df['SLG']).round(3)
    df['Season'] = year
    dfs[year] = df

train_years = [2017, 2018, 2019, 2021, 2022, 2023]
train_df = pd.concat(dfs[year] for year in train_years)
train_df = train_df.drop_duplicates()

train_df.to_csv('data/training.csv')

# Create y

y = train_df.OPS

# Create X

feature_names = ["K%", "BB%", "xBA", "xwOBA", "xSLG", "Whiff%", "LA (°)",  "Hard Hit%",
                 "Barrel/BBE%", "EV (MPH)"]

X = train_df[feature_names]


# Set up simple DecisionTree model

from sklearn.tree import DecisionTreeRegressor
ops_model = DecisionTreeRegressor(random_state = 1)
ops_model.fit(X, y)

predictions = ops_model.predict(X)


# Calculate in-sample error

from sklearn.metrics import mean_absolute_error, r2_score
print(mean_absolute_error(y, predictions))
print(r2_score(y, predictions))


# Use split data to check for 

from sklearn.model_selection import train_test_split

train_X, val_X, train_y, val_y = train_test_split(X, y, random_state= 0)
ops_split_model = DecisionTreeRegressor()
ops_split_model.fit(train_X, train_y)
split_predictions = ops_split_model.predict(val_X)
print(mean_absolute_error(val_y, split_predictions))
print(r2_score(val_y, split_predictions))


# Test on 2024 data

y_2024 = dfs[2024].OPS
X_2024 = dfs[2024][feature_names]

# Found most accurate num_nodes, difference was negligible

# def get_mae(num_nodes, train_X, val_X, train_y, val_y):
#     model = DecisionTreeRegressor(max_leaf_nodes=num_nodes, random_state = 0)
#     model.fit(train_X, train_y)
#     the_prediction = model.predict(val_X)
#     mae = mean_absolute_error(val_y, the_prediction)
#     return(mae)

# for num_nodes in range(2, 5000):
#     lowest_mae = 1000
#     if (get_mae(num_nodes, train_X, val_X, train_y, val_y) < lowest_mae):
#         lowest_mae = get_mae(num_nodes, train_X, val_X, train_y, val_y)
#         lowest_num_nodes = num_nodes

# print(lowest_mae)
# print(lowest_num_nodes)


predictions_2024 = ops_model.predict(X_2024)
print(mean_absolute_error(y_2024, predictions_2024))
print(r2_score(y_2024, predictions_2024))


# Decision Tree was not accurate enough, try Random Forest

from sklearn.ensemble import RandomForestRegressor

ops_forest = RandomForestRegressor(random_state=1)
ops_forest.fit(X, y)
print("Random Forest training results: ")
forest_predictions = ops_forest.predict(X)
print(mean_absolute_error(y, forest_predictions))
print(r2_score(y, forest_predictions))

forest_2024 = ops_forest.predict(X_2024)
print("\n2024 Random Forest results: ")
print(mean_absolute_error(y_2024, forest_2024))
print(r2_score(y_2024, forest_2024))

print("\n")


# Apply model to 2025 data, negative means hitter has been unlucky,
# while positive means that hitter has been lucky.

y_2025 = dfs[2025].OPS
X_2025 = dfs[2025][feature_names]

predictions_2025 = ops_forest.predict(X_2025)
dfs[2025]['Predicted_OPS'] = predictions_2025.round(3)

ops_diff_list = []

def get_ops_diff(the_row):
    ops_diff = the_row['OPS'] - the_row['Predicted_OPS']
    ops_diff_list.append(round(ops_diff,3))


for index, row in dfs[2025].iterrows():
    get_ops_diff(row)

dfs[2025]["OPS Diff"] = ops_diff_list

dfs[2025] = dfs[2025].sort_values('OPS Diff')

dfs[2025]

dfs[2025].to_csv('data/ops_diff_2025.csv', index=False)


# Trying XGBoost to improve accuracy

from xgboost import XGBRegressor

xgb_model = XGBRegressor()

xgb_model.fit(X, y)

xgb_2024 = xgb_model.predict(X_2024)
print("\n2024 XGBoostRegressor results: ")
print(mean_absolute_error(y_2024, xgb_2024))
print(r2_score(y_2024, xgb_2024))


# Also trying LightGBM 

import lightgbm

gbm_model = lightgbm.LGBMRegressor()

gbm_model.fit(X, y, eval_set=[(X_2024, y_2024)])

gbm_2024 = xgb_model.predict(X_2024)
print("\n2024 LightGBMRegressor results: ")
print(mean_absolute_error(y_2024, gbm_2024))
print(r2_score(y_2024, gbm_2024))


# Random Forest feature inportance
model_importances = ops_forest.feature_importances_
feature_imp_df = pd.DataFrame({'Feature': feature_names, 'Importance': model_importances}).sort_values('Importance', ascending=False)
print(feature_imp_df)


