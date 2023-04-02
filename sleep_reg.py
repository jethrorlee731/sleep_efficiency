
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import r2_score
import pandas as pd
import sleep

def disp_regress(df, x_feat_list, y_feat, verbose=True):
    """ linear regression, displays model w/ coef

    Args:
        df (pd.DataFrame): dataframe
        x_feat_list (list): list of all features in model
        y_feat (list): target feature
        verbose (bool): toggles command line output

    Returns:
        reg (LinearRegression): model fit to data
    """
    # initialize regression object
    reg = LinearRegression()

    # get target variable
    # (note: since we index with list -> garauanteed 2d x array, no reshape needed)
    x = df.loc[:, x_feat_list].values
    y = df.loc[:, y_feat].values

    # fit regression
    reg.fit(x, y)

    # compute / store r2
    y_pred = reg.predict(x)

    if verbose:
        # print model
        model_str = y_feat + f' = {reg.intercept_:.2f}'
        for feat, coef in zip(x_feat_list, reg.coef_):
            s_sign = ' - ' if coef < 0 else ' + '
            model_str += s_sign + f'{np.abs(coef):.2f} {feat}'
        print(model_str)

        # compute / print r2
        r2 = r2_score(y_true=y, y_pred=y_pred)
        print(f'r2 = {r2:.3} (not cross validated)')

    return reg

def main():
    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage']

    # load sleep data
    df_sleep = pd.read_csv('data/Sleep_Efficiency.csv')
    df_sleep.dropna(axis=0, inplace=True)

    # parse the bedtime columns to only include hours into the day
    df_sleep = sleep.parse_times(df_sleep, 'Bedtime')

    # parse the wakeup time columns to only include hours into the day
    df_sleep = sleep.parse_times(df_sleep, 'Wakeup time')

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender', 'Smoking status'], drop_first=True)
    print(df_sleep.columns)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    disp_regress(df=df_sleep, x_feat_list=x_feat_list, y_feat='Sleep efficiency');
    disp_regress(df=df_sleep, x_feat_list=x_feat_list, y_feat='REM sleep percentage');
    disp_regress(df=df_sleep, x_feat_list=x_feat_list, y_feat='Deep sleep percentage');


if __name__ == '__main__':
    main()