"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_mult_reg.py)
April 19, 2023

sleep_mult_reg.py: Using a multiple linear regression model to predict sleep efficiency, REM sleep percentages, and deep
                   sleep percentages

This file presents how the r2 for when the multiple linear regression model predicts sleep efficiency,
REM sleep percentage, and deep sleep percentage is lower than that for the random forest regressor

The r^2 value of the multiple regression model hovers around 0.52 (sleep efficiency), 0.08 (REM sleep percentage),
0.27 (Deep sleep percentage).
"""

# import statements
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import utils

def mult_reg(df, x_feat_list, y_feat):
    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we are indexing the x features with a list -> the array for the independent features is guaranteed to
    # be two-dimensional and not require reshaping)
    x = df.loc[:, x_feat_list].values
    y = df.loc[:, y_feat].values

    # fit the multiple regression model
    reg.fit(x, y)

    # the machine learning model makes predictions based on the values inputted by the user
    y_pred = reg.predict(x)

    # compute / print r2
    r_squared = r2_score(y_true=y, y_pred=y_pred)

    return r_squared

def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    df_sleep, x_feat_list = utils.get_x_feat(EFFICIENCY)

    r2_eff = mult_reg(df_sleep, x_feat_list, 'Sleep efficiency')
    r2_rem = mult_reg(df_sleep, x_feat_list, 'REM sleep percentage')
    r2_deep = mult_reg(df_sleep, x_feat_list, 'Deep sleep percentage')

    print('The r2 for predicting Sleep efficiency is', r2_eff)
    print('The r2 for predicting REM sleep percentage is', r2_rem)
    print('The r2 for predicting Deep sleep percentage is', r2_deep)

    # try to only use top 3 features (based on random forest regressor) from each initial model
    i_r2_eff = mult_reg(df_sleep, ['Awakenings', 'Age', 'Alcohol consumption 24 hrs before'
                                                                           ' sleeping (oz)'], 'Sleep efficiency')
    i_r2_rem = mult_reg(df_sleep, ['Age', 'Wakeup time', 'Bedtime'],
                                                     'REM sleep percentage')
    i_r2_deep = mult_reg(df_sleep, ['Alcohol consumption 24 hrs before sleeping (oz)', 'Age',
                                                        'Awakenings'], 'Deep sleep percentage')

    print('The improved r2 for predicting Sleep efficiency is', i_r2_eff)
    print('The improved r2 for predicting REM sleep percentage is', i_r2_rem)
    print('The improved r2 for predicting Deep sleep percentage is', i_r2_deep)

    # It appears that just using the top 3 features actually makes the models worse. Additionally, all the models
    # made in this multiple linear regression are worse than those made using random forest regressor (comparing like
    # models). Therefore, for our sleep predictor model in utils.py and sleep.py, we will only use the random forest
    # regressor.


if __name__ == '__main__':
    main()
