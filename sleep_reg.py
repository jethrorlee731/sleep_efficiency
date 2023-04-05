# THIS PY FILE IS NOT BEING USED. I MOVED THE REG HERE TO THE SLEEP.PY.

from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import r2_score
import pandas as pd
import sleep


def main():
    # Establish the features not used by the multiple linear regression
    # Sleep duration is not used because it is calculated based on wakeup time minus bedtime
    unwanted_feats = ['ID', 'Sleep efficiency', 'Sleep duration']

    # load sleep data
    df_sleep = pd.read_csv('data/Sleep_Efficiency.csv')
    df_sleep.dropna(axis=0, inplace=True)

    # parse the bedtime columns to only include hours into the day
    df_sleep = sleep._parse_times(df_sleep, 'Bedtime')

    # parse the wakeup time columns to only include hours into the day
    df_sleep = sleep._parse_times(df_sleep, 'Wakeup time')

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender', 'Smoking status'], drop_first=True)
    print(df_sleep.columns)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we index with list -> guaranteed 2d x array, no reshape needed)
    x = df_sleep.loc[:, x_feat_list].values
    y = df_sleep.loc[:, 'Sleep efficiency'].values

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
    # r_squared = r2_score(y_true=y, y_pred=y_pred)
    # print(f'r2 = {r_squared:.3} (not cross validated)')


if __name__ == '__main__':
    main()