"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (random_forest_assets.py)
April 19, 2023

random_forest_assets.py: Generic functions associated with random forest regressors and feature importance metrics
"""
# import statements
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import plotly.express as px
import utils


def forest_reg(focus_col, df):
    """ Builds a random forest regressor model that predicts a y-variable
    Args:
        focus_col (str): name of the y-variable of interest
        df (pd.DataFrame): dataframe of interest that contains data used to train the regressor
    Returns:
        random_forest_reg: fitted random forest regressor that predicts the y-variable based on the inputted data set
    """
    # retrieve the x features for the random forest regressor
    df, x_feat_list = utils.get_x_feat(df)

    # extract data from dataframe
    x = df.loc[:, x_feat_list].values
    y = df.loc[:, focus_col].values

    # initialize a random forest regressor
    random_forest_reg = RandomForestRegressor()

    # fit the data extracted from the data frame
    random_forest_reg.fit(x, y)

    return random_forest_reg


def plot_feat_import_rf_reg(feat_list, feat_import, sort=True, limit=None):
    """ plots feature importance values in a horizontal bar chart

    The x-axis is labeled accordingly for a random forest regressor

    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importance values (mean MSE reduce)
        sort (bool): if True, sorts features in decreasing importance from top to bottom of plot
        limit (int): if passed, limits the number of features shown to this value
    Returns:
        fig (px.bar): the feature importance bar chart
    """
    if sort:
        # sort features by decreasing importance
        idx = np.argsort(feat_import).astype(int)
        feat_list = [feat_list[_idx] for _idx in idx]
        feat_import = feat_import[idx]

    if limit is not None:
        # limit to the first limit feature
        feat_list = feat_list[:limit]
        feat_import = feat_import[:limit]

    # plot the feature importance bar chart
    fig = px.bar(x=feat_list, y=feat_import, labels={'x': 'Features', 'y': 'feature importance'},
                 template='plotly_dark', height=600)

    return fig
