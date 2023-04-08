"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (utils.py)
April 19, 2023

utils.py: Helper functions for sleep.py
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import plotly.express as px


def read_file(filename):
    """ Read in the file interested in, convert to dataframe, and do some cleaning
    Args:
        filename (str): name of interested file
    Returns:
        file_copy (dataframe): cleaned dataframe
    """
    # read the csv files into dataframes
    file = pd.read_csv(filename)

    # make a copy of the file
    file_copy = file.copy()

    # drop rows with NA values
    file_copy = file_copy.dropna()

    # multiply sleep efficiencies by 100 to represent them as percentages
    file_copy.loc[:, 'Sleep efficiency'] = file_copy['Sleep efficiency'] * 100

    # clarifying metrics
    file_copy = file_copy.rename(columns={'Exercise frequency': 'Exercise frequency (in days per week)'})

    return file_copy


def parse_times(df_sleep):
    """ Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
    Returns:
        df_sleep (Pandas data frame): a newer version of the data frame with the parsed times
    """
    # parse the bedtime columns to only include hours into the day (military time)
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str.split().str[1]
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / 60

    # parse the wakeup time columns to only include hours into the day (military time)
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
                              df_sleep['Wakeup time'].str[3:5].astype(float) / 60
    return df_sleep


def filt_vals(df, vals, col, lcols):
    """ Filter the user-selected values from the dataframe
    Args:
        df: (dataframe) a dataframe with the values we are seeking and additional attributes
        vals (list): two user-defined values, a min and max
        col (str): the column to filter by
        lcols (list): a list of column names to return
    Returns:
        df_update (dataframe): the dataframe filtered to just include the values within the user specified range
    """
    # identify the beginning and end of the range
    least = vals[0]
    most = vals[1]

    # filter out the rows for which the column values are within the range
    df_update = df[df[col].between(least, most)][lcols]

    # return the updated dataframe to user
    return df_update


def forest_reg(focus_col, data):
    """ Builds the random forest regressor model that predicts a y-variable
    Args:
        focus_col (str): name of the y-variable of interest
        data (pd.DataFrame): dataframe of interest
    Returns:
        random_forest_reg: fitted random forest regressor based on the dataset
    """
    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=data, columns=['Gender', 'Smoking status'], drop_first=True)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # extract data from dataframe
    x = df_sleep.loc[:, x_feat_list].values
    y = df_sleep.loc[:, focus_col].values

    # initialize a random forest regressor
    random_forest_reg = RandomForestRegressor()

    random_forest_reg.fit(x, y)

    return random_forest_reg


def convert(gender, smoke):
    """ Encode the passed in variables to match encoding in the random forest regressor
    Args:
        gender (str): whether the user is Biological Male or Biological Female
        smoke (str): whether the user smokes or not
    Returns:
        gender_value (int): encoded variable representing gender of the user
        smoke_value (int): encoded variable representing whether the user smokes
    """
    if gender == 'Biological Male':
        gender_value = 1
    else:
        gender_value = 0

    if smoke == 'Yes':
        smoke_value = 1
    else:
        smoke_value = 0

    return gender_value, smoke_value


def plot_feat_import_rf_reg(feat_list, feat_import, sort=True, limit=None):
    """ plots feature importances in a horizontal bar chart

    The x-axis is labeled accordingly for a random forest regressor

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

    fig = px.bar(x=feat_list, y=feat_import, labels={'x': 'Features', 'y': 'feature importance'},
                 template='plotly_dark')

    return fig


def predict_sleep_quality(sleep_quality_stat, df_sleep, age, bedtime, wakeuptime, duration, awakenings, caffeine,
                          alcohol, exercise, gender, smoke):
    """ Allow users to get their predicted sleep quality given information about a user
    Args:
        sleep_quality_stat (str): the sleep statistic to be predicted for the user
        df_sleep (pandas df): data frame containing information about the sleep quality of multiple individuals
        age (int): the age of the user
        bedtime (float): user's bedtime based on hours into the day (military time)
        wakeuptime (float): user's wakeup time based on hours into the day (military time)
        duration (float): number of hours that the user was asleep (wakeup time minus bedtime)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine a user consumes in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol a user consumes in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted sleep efficiency
    """
    # Builds the random forest regressor model that predicts a user's sleep efficiency, REM sleep percentage, or deep
    # sleep percentage
    random_forest_reg = forest_reg(sleep_quality_stat, df_sleep)

    # Encode the passed-in values for gender and smoking status to match the encoding in the random forest regressor
    gender_value, smoke_value = convert(gender, smoke)

    # convert the user inputs  into a numpy array
    data = np.array([[age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise,
                      gender_value, smoke_value]])

    # predict sleep efficiency, REM sleep percentage, or deep sleep percentage based on user inputs from the dropdown
    # and sliders
    y_pred = random_forest_reg.predict(data)

    return y_pred


def _encode(var1, var2, df_sleep):
    """
    Encodes quantitative binary variables to qualitative variables via one-hot encoding

    Args:
        var1 (str): one variable that may contain binary data in a dataframe
        var2 (str): another variable that may contain binary data in the dataframe
        df_sleep (Pandas df): data frame containing information about the sleep quality of multiple individuals

    Returns:
        df (Pandas df): a new version of the data frame that contains the encoded columns (if they get encoded)
    """
    # saving column names into constants
    GENDER_COL = 'Gender'
    SMOKING_COL = 'Smoking status'

    # performing one hot encoding on the gender column (a binary variable) to make it quantitative instead of
    # qualitative if it's needed for the plot
    if var1 == GENDER_COL or var2 == GENDER_COL:
        df_sleep = pd.get_dummies(data=df_sleep, columns=[GENDER_COL], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Gender_Male': 'Gender'})

    # performing one hot encoding on the smoking status column (a binary variable) to make it quantitative instead of
    # qualitative if it's needed for the plot
    if var1 == SMOKING_COL or var2 == SMOKING_COL:
        df_sleep = pd.get_dummies(data=df_sleep, columns=[SMOKING_COL], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    return df_sleep
