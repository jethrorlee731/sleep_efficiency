"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_reg.py)
April 19, 2023

sleep_reg.py: Using a multiple linear regression model to predict sleep efficiency, REM sleep percentages, and deep
              sleep percentages

A random forest regressor is already built in the utils.py file. This file presents how the r^2 for when the regressor
predicts sleep efficiency, REM sleep percentage, and deep sleep percentage is higher than that for the multiple linear
regression model. Combined with how the multiple linear regression model uses the same data to train and predict and
that the multiple linear regression model cannot even be shown on the dashboard, we decided to only use the random
forest regressor.
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import utils

def main():
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    EFFICIENCY = utils.parse_times(EFFICIENCY)

    # Establish the features not used by the muliple linear regression
    # Sleep duration is not used because it is calculated based on wakeup time minus bedtime
    unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    EFFICIENCY = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)
    # print(df_sleep.columns)

    # the x features for the regressor should be quantitative
    x_feat_list = list(EFFICIENCY.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)
    print(x_feat_list)

    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we index with list -> guaranteed 2d x array, no reshape needed)
    x = EFFICIENCY.loc[:, x_feat_list].values
    y = EFFICIENCY.loc[:, 'Deep sleep percentage'].values

    # fit regression
    reg.fit(x, y)

    # X HERE CAN BE WHAT THE USER CAN PASS IN BASED ON DASHBOARD INPUTS
    # compute / store r2
    y_pred = reg.predict(x)

    # # compute / print r2
    r_squared = r2_score(y_true=y, y_pred=y_pred)
    print(r_squared)
    # print(f'r2 = {r_squared:.3} (not cross validated)')


if __name__ == '__main__':
    main()