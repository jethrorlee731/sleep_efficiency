"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_forest.py)
April 19, 2023

sleep_forest.py: Building a random forest regressor to determine the attributes that best determine one's sleep
                 efficiency, REM sleep percentage, and deep sleep percentage

This file presents how the r^2 value for when the regressor predicts sleep efficiency, REM sleep percentage,
and deep sleep percentage is higher than that for multiple linear regression models predicting the same values.

Note that the random forest regressor used for the project is directly implemented in the sleep.py and
random_forest_assets.py file. This file just provides why we favored using a random forest regressor (higher r^2)
over multiple linear regression.

The r^2 value of this random forest regressor hovers around 0.67 for predicting sleep efficiency, 0.16 for predicting
REM sleep percentage, and 0.35 for predicting deep sleep percentage.

It appears that just using the top 3 important features to make predictions actually makes the random forest
regressors worse (lower cross-validated r^2). Therefore, we used all the variables in the random forest regressors when
we made the sleep predictor in sleep.py and random_forest_assets.py"""

# Import statements
import numpy as np
from sklearn.model_selection import KFold
from copy import copy
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict
import utils


def map_feature_import_vals(feat_list, feat_import, sort=True, limit=None):
    """ Map features to their importance metrics
    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importance values (mean MSE reduce)
        sort (bool): if True, sorts features in decreasing importance from top to bottom of plot
        limit (int): if passed, limits the number of features shown to this value
    Returns:
        feature_rank (list): has tuples that map certain features to their feature importance (mean MSE reduce) values
    """
    # initialize a dictionary that maps features to their importance metrics
    feature_rank = defaultdict(lambda: 0)

    if sort:
        # sort features in decreasing importance
        idx = np.argsort(feat_import).astype(int)
        feat_list = [feat_list[_idx] for _idx in idx]
        feat_import = feat_import[idx]

    if limit is not None:
        # limit to the first limit feature
        feat_list = feat_list[:limit]
        feat_import = feat_import[:limit]

    # create a list of tuples mapping features to their feature importance values
    for i in range(len(feat_list)):
        feature_rank[feat_list[i]] = feat_import[i]
    feature_rank = dict(feature_rank)
    feature_rank = sorted(feature_rank.items(), key=lambda item: item[1], reverse=True)

    # return a list of tuples mapping features to their feature importance values
    return feature_rank


def random_forest(x_feat_list, df, y_feat):
    """ Build a random forest regressor by training and testing it and compute its cross-validated r^2 score
    Args:
        x_feat_list (list): list of x-variables of interest (basis of training data)
        df (Pandas dataframe): a data frame containing data used to help the random forest regressor make predictions
        y_feat (str): y-variable of interest (the testing value)
    Return:
        r_squared (float): cross-validated r^2 score of the model
        importance_metrics (list): has tuples that map certain features to their feature importance (mean MSE reduce)
                                   values
    """
    # define the testing value
    y_feat = y_feat

    # extract data from dataframe
    x = df.loc[:, x_feat_list].values
    y = df.loc[:, y_feat].values

    # initialize a random forest regressor
    random_forest_reg = RandomForestRegressor()
    y_true = y

    # Cross-validation:
    # construction of (non-stratified) kfold object
    kfold = KFold(n_splits=10, shuffle=True)

    # allocate an empty array to store predictions in
    y_pred = copy(y_true)

    for train_idx, test_idx in kfold.split(x, y_true):
        # build arrays which correspond to x, y train /test
        x_test = x[test_idx, :]
        x_train = x[train_idx, :]
        y_true_train = y_true[train_idx]

        # fit happens "inplace", we modify the internal state of random_forest_reg to remember all the training samples;
        # gives the regressor the training data
        random_forest_reg.fit(x_train, y_true_train)

        # estimate the class of each test value
        y_pred[test_idx] = random_forest_reg.predict(x_test)

    # computing cross-validated R2 from sklearn
    r_squared = r2_score(y_true=y_true, y_pred=y_pred)

    # creates a list of tuples that map features to their importance value
    importance_metrics = map_feature_import_vals(x_feat_list, random_forest_reg.feature_importances_)

    return r_squared, importance_metrics


def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    # retrieve the values used to help the random forest regressors predict sleep efficiency, REM sleep percentage, and
    # deep sleep percentage
    df_sleep, x_feat_list = utils.get_x_feat(EFFICIENCY)

    # retrieve the r^2 values and the feature importance values associated with the random forest regressors and their
    # predictions about sleep efficiency, REM sleep percentage, and deep sleep percentage
    r2_sleep_eff, importance_eff = random_forest(x_feat_list, df_sleep, 'Sleep efficiency')
    r2_rem_sleep, importance_rem = random_forest(x_feat_list, df_sleep, 'REM sleep percentage')
    r2_deep_sleep, importance_deep = random_forest(x_feat_list, df_sleep, 'Deep sleep percentage')

    # print the cross-validated r^2 values and feature importance metrics
    print('The cross-validated r2 for predicting sleep efficiency is', r2_sleep_eff, 'and the feature importance '
                                                                                     'values of the x-variables in '
                                                                                     'descending order is',
          importance_eff)
    print('The cross-validated r2 for predicting REM sleep percentage is', r2_rem_sleep, 'and the feature importance '
                                                                                         'values of the x-variables in '
                                                                                         'descending order is',
          importance_rem)
    print('The cross-validated r2 for predicting deep sleep percentage is', r2_deep_sleep, 'and the feature importance '
                                                                                           'values of the x-variables '
                                                                                           'in descending order is',
          importance_deep)

    # random forest regressor using the top 3 features from each initial model to predict sleep efficiency, REM sleep
    # percentage, and deep sleep percentage
    i_r2_sleep_eff, i_importance_eff = random_forest(['Awakenings', 'Age', 'Alcohol consumption 24 hrs before'
                                                      ' sleeping (oz)'], df_sleep, 'Sleep efficiency')
    i_r2_rem_sleep, i_importance_rem = random_forest(['Age', 'Wakeup time', 'Bedtime'], df_sleep,
                                                     'REM sleep percentage')
    i_r2_deep_sleep, i_importance_deep = random_forest(['Alcohol consumption 24 hrs before sleeping (oz)', 'Age',
                                                        'Awakenings'], df_sleep, 'Deep sleep percentage')

    # print the cross-validated r^2 values for the models just using the critical features
    print('The cross-validated r2 for predicting sleep efficiency with just the critical features is', i_r2_sleep_eff)
    print('The cross-validated r2 for predicting REM sleep percentage with just the critical features is',
          i_r2_rem_sleep)
    print('The cross-validated r2 for predicting deep sleep percentage with just the critical features is',
          i_r2_deep_sleep)


if __name__ == '__main__':
    main()
