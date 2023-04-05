# THIS PY FILE IS NOT BEING USED. I MOVED THE REG HERE TO THE SLEEP.PY.

from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import r2_score
import pandas as pd
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
    else:
        None

    return df_sleep




# parse the Bedtime and Wakeup time for the EFFICIENCY dataframe
# _parse_times(EFFICIENCY, "Bedtime")
# _parse_times(EFFICIENCY, 'Wakeup time')

def main():
    # Establish the features not used by the muliple linear regression
    # Sleep duration is not used because it is calculated based on wakeup time minus bedtime
    unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']
    # unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
    #                   'Light sleep percentage', 'Gender', 'Smoking status', 'Exercise frequency', 'Wakeup time',
    #                   'Bedtime', 'Caffeine consumption', 'Age', 'Alcohol consumption', 'Awakenings']
    # unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
    #                   'Light sleep percentage', 'Gender_Male',
    #                 'Caffeine consumption']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    EFFICIENCY = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)
    # print(df_sleep.columns)
    _parse_times(EFFICIENCY, "Bedtime")
    _parse_times(EFFICIENCY, 'Wakeup time')

    # the x features for the regressor should be quantitative
    x_feat_list = list(EFFICIENCY.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)
    print(x_feat_list)
    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we index with list -> guaranteed 2d x array, no reshape needed)
    x = EFFICIENCY.loc[:, x_feat_list].values
    y = EFFICIENCY.loc[:, 'Deep sleep percentage'].values

    # fit regression
    reg.fit(x, y)

    # X HERE CAN BE WHAT THE USER CAN PASS IN BASED ON DASHBOARD INPUTS
    # compute / store r2
    y_pred = reg.predict(x)

    # # print model
    # model_str = 'Sleep efficiency' + f' = {reg.intercept_:.2f}'
    # for feat, coef in zip(x_feat_list, reg.coef_):
    #     s_sign = ' - ' if coef < 0 else ' + '
    #     model_str += s_sign + f'{np.abs(coef):.2f} {feat}'
    # print(model_str)
    #
    # # compute / print r2
    r_squared = r2_score(y_true=y, y_pred=y_pred)
    print(r_squared)
    # print(f'r2 = {r_squared:.3} (not cross validated)')


if __name__ == '__main__':
    main()