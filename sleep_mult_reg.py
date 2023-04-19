"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_mult_reg.py)
April 19, 2023

sleep_mult_reg.py: Using a multiple linear regression model to predict sleep efficiency, REM sleep percentages, and deep
                   sleep percentages

This file presents how the R^2 value for when the multiple linear regression model predicts sleep efficiency,
REM sleep percentage, and deep sleep percentage is lower than that for the random forest regressor

The R^2 value of the multiple regression model hovers around 0.52 for predicting sleep efficiency, 0.08 for predicting
REM sleep percentage, and 0.27 for predicting deep sleep percentage

It appears that just using the top 3 features indicated by a random forest regressor for predicting sleep efficiency,
REM sleep percentage, and deep sleep percentage actually makes the regression models worse (lower R^2 values).
Additionally, all the created multiple linear regression models yield lower R^2 values than a corresponding random
forest regressor that predicts the same value. Therefore, our sleep predictors in random_forest_assets.py and sleep.py
only use a random forest regressor. """

# import statements
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import utils


def mult_reg(df, x_feat_list, y_feat):
    """
    Computes the r^2 value of a multiple regression model

    Args:
        df (Pandas data frame): a dataframe containing data of interest
        x_feat_list (list of strings): a list of columns containing data that helps the model make predictions
        y_feat (string): the target variable of interest

    Returns:
        r_squared (float): the r^2 value associated with how well the model makes its predictions
    """
    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we are indexing the x features with a list, the array for the independent features is guaranteed to
    # be two-dimensional and not require reshaping)
    x = df.loc[:, x_feat_list].values
    y = df.loc[:, y_feat].values

    # fit the multiple regression model
    reg.fit(x, y)

    # the machine learning model makes predictions based on the values inputted by the user
    y_pred = reg.predict(x)

    # compute r^2, which will get returned
    r_squared = r2_score(y_true=y, y_pred=y_pred)

    return r_squared


def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    # extract the values used to help the multiple regression models predict sleep efficiency, REM sleep percentage, and
    # deep sleep percentage
    df_sleep, x_feat_list = utils.get_x_feat(EFFICIENCY)

    # calculate the r^2 values associated with the ability of multiple regression models to predict a user's sleep
    # efficiency, REM sleep percentage, and deep sleep percentage
    r2_eff = mult_reg(df_sleep, x_feat_list, 'Sleep efficiency')
    r2_rem = mult_reg(df_sleep, x_feat_list, 'REM sleep percentage')
    r2_deep = mult_reg(df_sleep, x_feat_list, 'Deep sleep percentage')

    # print the r^2 values
    print('The r2 for predicting sleep efficiency is', r2_eff)
    print('The r2 for predicting REM sleep percentage is', r2_rem)
    print('The r2 for predicting deep sleep percentage is', r2_deep)

    # using only the top 3 features (based on a random forest regressor) for the multiple regression model to predict a
    # user's sleep efficiency, REM sleep percentage, and deep sleep percentage
    i_r2_eff = mult_reg(df_sleep, ['Awakenings', 'Age', 'Alcohol consumption 24 hrs before sleeping (oz)'],
                                   'Sleep efficiency')
    i_r2_rem = mult_reg(df_sleep, ['Age', 'Wakeup time', 'Bedtime'], 'REM sleep percentage')
    i_r2_deep = mult_reg(df_sleep, ['Alcohol consumption 24 hrs before sleeping (oz)', 'Age', 'Awakenings'],
                                    'Deep sleep percentage')

    # print the r^2 values for the models just using the critical features
    print('The r2 for predicting sleep efficiency with just the critical features is', i_r2_eff)
    print('The r2 for predicting REM sleep percentage with just the critical features is', i_r2_rem)
    print('The r2 for predicting deep sleep percentage wit just the critical features is', i_r2_deep)


if __name__ == '__main__':
    main()
