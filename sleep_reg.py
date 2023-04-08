# WE ENDED UP NOT USING MULTIPLE LINEAR REGRESSION. RANDOM FOREST REGRESSOR HAD A BETTER R2 SCORE SO WE WENT WITH
# USING THAT MODEL TO MAKE SLEEP QUALITY PREDICTIONS. WE CAN EXPLAIN THIS IN THE WRITEUP.
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn.metrics import r2_score
import pandas as pd
import utils

def main():
    EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

    EFFICIENCY = utils.parse_times(EFFICIENCY)

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