# MOVED EVERYTHING TO SLEEP.PY. MIGHT MOVE IT BACK HERE AFTER EVERYTHING WORKS.
# THIS DOCUMENT IS ALSO NECESSARY TO SHOW THAT THE RANDOM FOREST REGRESSOR MODEL IS ALRIGHT IN PREDICTING SLEEP
# EFFICIENCY, REM SLEEP PERCENTAGE, AND DEEP SLEEP PERCENTAGE BASED ON THE CROSS VALIDATED R2 SCORE.
"""
Colbe Chang, Jocelyn Ju, Jethro Lee, Michelle Wang, Ceara Zhang
DS3500 / Final Project
Sleep Efficiency Dashboard
Date Created: 3/30/23
Last Updated: 4/6/2023
"""

"""
sleep_forest.py: Build a random forest regressor to determine the attributes that best determine one's sleep
                     efficiency
"""

# Import statements
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from copy import copy
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from collections import defaultdict

efficiency = pd.read_csv('data/Sleep_Efficiency.csv')
# I JUST DID THIS FOR NOW SO WE DON'T RUN INTO ISSUES WITH NA VALUES BELOW. WE CAN FIX THIS BY REPLACING WITH MEDIAN
# OF THE COLUMN IF WE WANT.
EFFICIENCY = efficiency.dropna()

def _parse_times(df_sleep, sleep_stat):
    """ Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
        sleep_stat (str): The statistic to be portrayed on the box plot
    Returns:
        sleep_df (Pandas data frame): a newer version of the data frame with the parsed times
    """
    # parse the bedtime columns to only include hours into the day
    if sleep_stat == 'Bedtime':
        df_sleep['Bedtime'] = df_sleep['Bedtime'].str.split().str[1]
        df_sleep['Bedtime'] = df_sleep['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / \
                              60

    # parse the wakeup time columns to only include hours into the day
    elif sleep_stat == 'Wakeup time':
        df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
        df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
                                  df_sleep['Wakeup time'].str[3:5].astype(float) / 60

    # Parse no data if neither the bedtime or wakeup time columns are specified via the sleep_stat parameter
    # else:
    #     None

    return df_sleep


# def plot_feat_import_rf_reg(feat_list, feat_import, sort=True, limit=None):
#     """ plots feature importances in a horizontal bar chart
#
#     The x axis is labeled accordingly for a random forest regressor
#
#     Args:
#         feat_list (list): str names of features
#         feat_import (np.array): feature importances (mean MSE reduce)
#         sort (bool): if True, sorts features in decreasing importance
#             from top to bottom of plot
#         limit (int): if passed, limits the number of features shown
#             to this value
#     Returns:
#         None, just plots the feature importance bar chart
#     """
#     if sort:
#         # sort features in decreasing importance
#         idx = np.argsort(feat_import).astype(int)
#         feat_list = [feat_list[_idx] for _idx in idx]
#         feat_import = feat_import[idx]
#
#     if limit is not None:
#         # limit to the first limit feature
#         feat_list = feat_list[:limit]
#         feat_import = feat_import[:limit]
#
#     # plot and label feature importance
#     plt.barh(feat_list, feat_import)
#     plt.gcf().set_size_inches(5, len(feat_list) / 2)
#     plt.xlabel('Feature importance\n(Mean decrease in MSE across all Decision Trees)')
#
#     # show the feature importance graph
#     plt.show()
#

def make_feature_import_dict(feat_list, feat_import, sort=True, limit=None):
    """ Map features to their importance metrics

    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importances (mean MSE reduce)
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

    # create a dictionary mapping features to their feature importances
    for i in range(len(feat_list)):
        feature_dict[feat_list[i]] = feat_import[i]
    feature_dict = dict(feature_dict)
    feature_dict = sorted(feature_dict.items(), key=lambda item: item[1], reverse=True)

    # return the feature importance dictionary
    return feature_dict


def main():

    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']
    # Establish the theme of any visualizations
    sns.set()

    # load sleep data
    df_sleep = pd.read_csv('data/Sleep_Efficiency.csv')
    df_sleep.dropna(axis=0, inplace=True)

    # parse the bedtime columns to only include hours into the day
    df_sleep = _parse_times(df_sleep, 'Bedtime')

    # parse the wakeup time columns to only include hours into the day
    df_sleep = _parse_times(df_sleep, 'Wakeup time')

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender', 'Smoking status'], drop_first=True)
    print(df_sleep.columns)

    # define the true and testing values

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

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

        # fit happens "inplace", we modify the internal state of
        # random_forest_reg to remember all the training samples;
        # gives the regressor the training data
        random_forest_reg.fit(x_train, y_true_train)

        # estimate the class of each test value
        y_pred[test_idx] = random_forest_reg.predict(x_test)

    # computing R2 from sklearn
    r_squared = r2_score(y_true=y_true, y_pred=y_pred)
    print(r_squared)
    # # show the cross validated r^2 value of the random forest regressor
    # print('Cross-validated r^2:', r_squared)

    # # creates a dictionary that maps features to their importance value
    # # THIS SHOULD MAKE BE SHOWED TO THE USER ALONG WITH THE PLOT
    sleep_important = make_feature_import_dict(x_feat_list, random_forest_reg.feature_importances_)
    print(sleep_important)
    #
    # # plots the importance of features in determining a person's sleep efficiency by the random forest regressor
    # plot_feat_import_rf_reg(x_feat_list, random_forest_reg.feature_importances_)
    # plt.gcf().set_size_inches(30, 30)


if __name__ == '__main__':
    main()
