"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_mult_reg.py)
April 19, 2023

sleep_mult_reg.py: Using a multiple linear regression model to predict sleep efficiency, REM sleep percentages, and deep
                   sleep percentages

A random forest regressor is already built in the utils.py file. This file presents how the r^2 for when the regressor
predicts sleep efficiency, REM sleep percentage, and deep sleep percentage is higher than that for the multiple linear
regression model. Combined with how the multiple linear regression model uses the same data to train and predict and
that the multiple linear regression model cannot even be shown on the dashboard, we decided to only use the random
forest regressor.

The r^2 value of the multiple regression model hovers around 0.27
"""

# import statements
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import utils


def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    # Establish the features not used by the multiple linear regression model (aka any features not inputted by the
    # user)
    unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    EFFICIENCY = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)
    # print(df_sleep.columns)

    # the x features for the regression model should be quantitative and not include the same features predicted by the
    # machine
    x_feat_list = list(EFFICIENCY.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we are indexing the x features with a list -> the array for the independent features is guaranteed to
    # be two-dimensional and not require reshaping)
    x = EFFICIENCY.loc[:, x_feat_list].values
    y = EFFICIENCY.loc[:, 'Deep sleep percentage'].values

    # fit the multiple regression model
    reg.fit(x, y)

    # the machine learning model makes predictions based on the values inputted by the user
    y_pred = reg.predict(x)

    # compute / print r2
    r_squared = r2_score(y_true=y, y_pred=y_pred)
    print(r_squared)


if __name__ == '__main__':
    main()
