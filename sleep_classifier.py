# Build a random forest regressor to determine the attributes that best determine one's deep sleep percentage

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


def plot_feat_import_rf_reg(feat_list, feat_import, sort=True, limit=None):
    """ plots feature importances in a horizontal bar chart

    The x axis is labeled accordingly for a random forest regressor

    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importances (mean MSE reduce)
        sort (bool): if True, sorts features in decreasing importance
            from top to bottom of plot
        limit (int): if passed, limits the number of features shown
            to this value
    Returns:
        None, just plots the feature importance bar chart
    """
    if sort:
        # sort features in decreasing importance
        idx = np.argsort(feat_import).astype(int)
        feat_list = [feat_list[_idx] for _idx in idx]
        feat_import = feat_import[idx]

    if limit is not None:
        # limit to the first limit feature
        feat_list = feat_list[:limit]
        feat_import = feat_import[:limit]

    # plot and label feature importance
    plt.barh(feat_list, feat_import)
    plt.gcf().set_size_inches(5, len(feat_list) / 2)
    plt.xlabel('Feature importance\n(Mean decrease in MSE across all Decision Trees)')

    # show the feature importance graph
    plt.show()


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


# Establish the theme of any visualizations
sns.set()

# load sleep data
df_sleep = pd.read_csv('data/Sleep_Efficiency.csv')
df_sleep.dropna(axis=0, inplace=True)

# we can represent binary categorical variables in single indicator tags
df_sleep['is_female'] = df_sleep['Gender'] == 'Female'
df_sleep['is_male'] = df_sleep['Gender'] == 'Male'
df_sleep['is_smoker'] = df_sleep['Smoking status'] == 'Yes'
df_sleep['is_not_smoker'] = df_sleep['Smoking status'] == 'No'

# define the true and testing values

# the x features for the regressor should be quantitative and meaningful (e.g., no one can control their light sleep
# percentages directly, so 'Light sleep percentage' is not included)
x_feat_list = ['Age', 'is_female', 'is_male', 'Sleep duration', 'Caffeine consumption', 'Alcohol consumption',
               'is_smoker', 'is_not_smoker', 'Exercise frequency']

y_feat = 'Deep sleep percentage'

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

# show the cross validated r^2 value of the random forest regressor
print('Cross-validated r^2:', r_squared)

# plots the importance of features in determining a person's deep sleep percentage by the random forest regressor
plot_feat_import_rf_reg(x_feat_list, random_forest_reg.feature_importances_)
plt.gcf().set_size_inches(15, 7)

# creates a dictionary that maps features to their importance value
deep_sleep_important = make_feature_import_dict(x_feat_list, random_forest_reg.feature_importances_)
print(deep_sleep_important)
