"""
sleep_forest.py: Build a random forest regressor to determine the attributes that best determine one's sleep
                     efficiency
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep_forest.py)
April 19, 2023

sleep_forest.py: Building a random forest regressor to determine the attributes that best determine one's sleep
                 efficiency, REM sleep percentage, and deep sleep percentage

A random forest regressor is already built in the utils.py file. This file presents how the r^2 for when the regressor
predicts sleep efficiency, REM sleep percentage, and deep sleep percentage is higher than that for the multiple linear
regression model.

Note that the random forest regressor used for the project is directly implemented in the sleep.py and utils.py file.
This is just the serve the purpose of proving why we used random forest regressor (higher r2) than multiple linear
regression.

The r^2 value of this random forest regressor hovers around 0.67 (sleep efficiency), 0.16 (REM sleep percentage),
0.35 (Deep sleep percentage)
"""
# Import statements
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from copy import copy
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict
import utils


def make_feature_import_dict(feat_list, feat_import, sort=True, limit=None):
    """ Map features to their importance metrics
    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importance values (mean MSE reduce)
        sort (bool): if True, sorts features in decreasing importance
            from top to bottom of plot
        limit (int): if passed, limits the number of features shown
            to this value
    Returns:
        feature_dict (list): has tuples that map certain features (key) to their feature importance (mean MSE reduce)
                             values
    """
    # initialize a dictionary that maps features to their importance metrics
    feature_dict = defaultdict(lambda: 0)

    if sort:
        # sort features in decreasing importance
        idx = np.argsort(feat_import).astype(int)
        feat_list = [feat_list[_idx] for _idx in idx]
        feat_import = feat_import[idx]

    if limit is not None:
        # limit to the first limit feature
        feat_list = feat_list[:limit]
        feat_import = feat_import[:limit]

    # create a dictionary mapping features to their feature importance values
    for i in range(len(feat_list)):
        feature_dict[feat_list[i]] = feat_import[i]
    feature_dict = dict(feature_dict)
    feature_dict = sorted(feature_dict.items(), key=lambda item: item[1], reverse=True)

    # return the feature importance dictionary
    return feature_dict

def random_forest(x_feat_list, df, y_feat):
    """ Build a random forest regressor by training and testing it and computed cross-validated r2 score
    Args:
        x_feat_list (list): list of x-variables of interest
        y_feat (str): interested y-variable
    Return:
        r_squared (float): cross-validated r2 score of the model
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

    # creates a dictionary that maps features to their importance value
    sleep_important = make_feature_import_dict(x_feat_list, random_forest_reg.feature_importances_)

    return r_squared, sleep_important

def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    df_sleep, x_feat_list = utils.get_x_feat(EFFICIENCY)

    r2_sleep_eff, importance_eff = random_forest(x_feat_list, df_sleep, 'Sleep efficiency')
    r2_rem_sleep, importance_rem = random_forest(x_feat_list, df_sleep, 'REM sleep percentage')
    r2_deep_sleep, importance_deep = random_forest(x_feat_list, df_sleep, 'Deep sleep percentage')

    print('The cross-validated r2 for predicting Sleep efficiency is', r2_sleep_eff, 'and the feature importance'
                                                                                     'of the x-variables in descending '
                                                                                     'order is',
          importance_eff)
    print('The cross-validated r2 for predicting REM sleep percentage is', r2_rem_sleep, 'and the feature importance '
                                                                                         'of the x-variables in '
                                                                                         'descending order is',
          importance_rem)
    print('The cross-validated r2 for predicting Deep sleep percentage is', r2_deep_sleep, 'and the feature importance, '
                                                                                           'of the x-variables in '
                                                                                           'descending order is',
          importance_deep)

    # random forest using the top 3 features from each initial model
    i_r2_sleep_eff, i_importance_eff = random_forest(['Awakenings', 'Age', 'Alcohol consumption 24 hrs before'
                                                                           ' sleeping (oz)'], df_sleep, 'Sleep efficiency')
    i_r2_rem_sleep, i_importance_rem = random_forest(['Age', 'Wakeup time', 'Bedtime'], df_sleep, 'REM sleep percentage')
    i_r2_deep_sleep, i_importance_deep = random_forest(['Alcohol consumption 24 hrs before sleeping (oz)', 'Age',
                                                        'Awakenings'], df_sleep, 'Deep sleep percentage')

    print('The improved cross-validated r2 for predicting Sleep efficiency is', i_r2_sleep_eff)
    print('The improved cross-validated r2 for predicting REM sleep percentage is', i_r2_rem_sleep)
    print('The improved cross-validated r2 for predicting Deep sleep percentage is', i_r2_deep_sleep)

    # It appears that just using the top 3 features actually makes the models worse. Therefore, we will stick with
    # using all the variables in the random forest regressor when we make the sleep predictor in sleep.py and utils.py

if __name__ == '__main__':
    main()
