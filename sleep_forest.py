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
regression model. Combined with how the multiple linear regression model uses the same data to train and predict and
that the multiple linear regression model cannot even be shown on the dashboard, we decided to only use the random
forest regressor.

The r^2 value of this random forest regressor hovers around 0.66
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


def main():
    # read in the sleep efficiency data frame, which contains information about the sleep quality of multiple subjects
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    # parse the bedtime and wakeup time columns to have them represented in military time
    EFFICIENCY = utils.parse_times(EFFICIENCY)

    # Establish the features not used by the random forest regressor (aka any features not inputted by the user)
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # Establish the theme of any visualizations
    sns.set()

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)
    print(df_sleep.columns)

    # define the true and testing values

    # the x features for the regressor should be quantitative and not include the same features predicted by the
    # regressor
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # define the testing value
    y_feat = 'Sleep efficiency'

    # extract data from dataframe
    x = df_sleep.loc[:, x_feat_list].values
    y = df_sleep.loc[:, y_feat].values

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

    # computing R2 from sklearn
    r_squared = r2_score(y_true=y_true, y_pred=y_pred)

    # # show the cross validated r^2 value of the random forest regressor
    print(r_squared)

    # # creates a dictionary that maps features to their importance value
    sleep_important = make_feature_import_dict(x_feat_list, random_forest_reg.feature_importances_)
    print(sleep_important)


if __name__ == '__main__':
    main()
