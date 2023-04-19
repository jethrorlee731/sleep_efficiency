"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (utils.py)
April 19, 2023

utils.py: Helper functions for sleep.py
"""
# import statements
import pandas as pd
import numpy as np
import random_forest_assets as rf


def read_file(filename):
    """ Read in a file, convert it to dataframe, and do some cleaning
    Args:
        filename (str): name of file of interest
    Returns:
        file_copy (Pandas data frame): cleaned dataframe containing the file's data
    """
    # read the CSV files into dataframes
    file = pd.read_csv(filename)

    # make a copy of the file
    file_copy = file.copy()

    # drop rows with NA values
    file_copy = file_copy.dropna()

    # multiply sleep efficiencies by 100 to represent them as percentages
    file_copy.loc[:, 'Sleep efficiency'] = file_copy['Sleep efficiency'] * 100

    # renaming columns to clarify metrics
    file_copy = file_copy.rename(columns={'Exercise frequency': 'Exercise frequency (in days per week)'})
    file_copy = file_copy.rename(columns={'Caffeine consumption': 'Caffeine consumption 24 hrs before sleeping (mg)'})
    file_copy = file_copy.rename(columns={'Alcohol consumption': 'Alcohol consumption 24 hrs before sleeping (oz)'})

    return file_copy


def parse_times(df_sleep):
    """ Parses the bedtime and wakeup time columns in the sleep data frame so they contain decimals that represent times
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
    Returns:
        df_sleep (Pandas data frame): a newer version of the data frame with the parsed times
    """
    # parse the bedtime columns to only include hours into the day (military time)
    df_sleep['Bedtime'] = df_sleep['Bedtime'].astype(str)
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str.split().str[1]
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / 60

    # parse the wakeup time columns to only include hours into the day (military time)
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].astype(str)
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
                              df_sleep['Wakeup time'].str[3:5].astype(float) / 60
    return df_sleep


def filt_vals(df, vals, col, lcols):
    """ Filter a dataframe by user-selected values
    Args:
        df: (Pandas dataframe) a dataframe with the values we are seeking and additional attributes
        vals (list of floats): two user-defined values, a min and max for "col"
        col (str): the column to filter by
        lcols (list of str): a list of column names to return
    Returns:
        df_updated (dataframe): the dataframe filtered, with just the values for "col" within the user specified range
    """
    # identify the beginning and end of the user-specified range for "col"
    least = vals[0]
    most = vals[1]

    # filter out the rows for which the column values are not within the range
    df_updated = df[df[col].between(least, most)][lcols]

    # return the updated dataframe to user
    return df_updated


def get_x_feat(df_sleep):
    """ Get desired x-features as a list - remove all other irrelevant; encode categorical variables and return new df
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
    Returns:
        df_sleep (pd.Dataframe): dataframe with categorical data encoded
        x_feat_list (list of str): list of desired x-variables
    """
    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender', 'Smoking status'], drop_first=True)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    return df_sleep, x_feat_list


def convert(gender, smoke):
    """ Encode passed-in variables to match the encoding of the random forest regressor
    Args:
        gender (str): indicates whether the user is a biological male or biological female
        smoke (str): indicates whether the user smokes or not
    Returns:
        gender_value (int): encoded variable representing the biological gender of the user
        smoke_value (int): encoded variable representing whether the user smokes
    """
    # encode the passed-in variable indicating a user's biological gender
    if gender == 'Biological Male':
        gender_value = 1
    else:
        gender_value = 0

    # encode the passed-in variable indicating a user's smoking status
    if smoke == 'Yes':
        smoke_value = 1
    else:
        smoke_value = 0

    return gender_value, smoke_value


def predict_sleep_quality(sleep_quality_stat, df_sleep, age, bedtime, wakeuptime, awakenings, caffeine, alcohol,
                          exercise, gender, smoke):
    """ Allow users to get their predicted sleep quality given information about them
    Args:
        sleep_quality_stat (str): the sleep statistic to be predicted for the user
        df_sleep (Pandas df): data frame containing information about the sleep quality of multiple individuals
        age (int): the age of the user
        bedtime (float): user's bedtime based on hours into the day (military time)
        wakeuptime (float): user's wakeup time based on hours into the day (military time)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine a user consumes in the 24 hours prior to their bedtime (in mg)
        alcohol (int): amount of alcohol a user consumes in the 24 hours prior to their bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted sleep efficiency/REM sleep percentage/deep sleep percentage
    """
    # Builds the random forest regressor model that predicts a user's sleep efficiency, REM sleep percentage, or deep
    # sleep percentage
    random_forest_reg = rf.forest_reg(sleep_quality_stat, df_sleep)

    # Encode the passed-in values for gender and smoking status to match the encoding of the random forest regressor
    gender_value, smoke_value = convert(gender, smoke)

    # calculate the sleep duration of a user based on their inputted bedtime and wakeup time
    if wakeuptime < bedtime:
        duration = wakeuptime + 24 - bedtime
    else:
        duration = wakeuptime - bedtime

    # store information about the user into a numpy array
    data = np.array([[age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise,
                      gender_value, smoke_value]])

    # predict sleep efficiency, REM sleep percentage, or deep sleep percentage based on user inputs from the dropdowns
    # and sliders
    y_pred = random_forest_reg.predict(data)

    return y_pred


def encode(var1, var2, df_sleep):
    """ Encodes quantitative binary variables as qualitative variables via one-hot encoding

    Args:
        var1 (str): one variable for a column that may contain binary data in a dataframe
        var2 (str): another variable for a column that may contain binary data in the dataframe
        df_sleep (Pandas df): data frame containing information about the sleep quality of multiple individuals

    Returns:
        df_sleep (Pandas df): a new version of the sleep data frame that contains any newly encoded columns
    """
    # saving column names into constants
    GENDER_COL = 'Gender'
    SMOKING_COL = 'Smoking status'

    # performing one hot encoding on the gender column (a binary variable) to make it quantitative instead of
    # qualitative if needed
    if var1 == GENDER_COL or var2 == GENDER_COL:
        df_sleep = pd.get_dummies(data=df_sleep, columns=[GENDER_COL], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Gender_Male': 'Gender'})

    # performing one hot encoding on the smoking status column (a binary variable) to make it quantitative instead of
    # qualitative if needed
    if var1 == SMOKING_COL or var2 == SMOKING_COL:
        df_sleep = pd.get_dummies(data=df_sleep, columns=[SMOKING_COL], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    return df_sleep
