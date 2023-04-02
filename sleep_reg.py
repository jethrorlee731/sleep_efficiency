
# linear regression model for bedtime(s), wake-up time(s), and sleep duration(s) associated with
# higher sleep efficiences, deep sleep percentages, and REM sleep percentages

# ALSO TRY MULTIPLE LINEAR REGRESSION!

from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

def show_fit(x, y, slope, intercept):
    plt.figure()

    # transform the input data into numpy arrays and flatten them for easier processing
    x = np.array(x).ravel()
    y = np.array(y).ravel()

    # plot the actual data
    plt.scatter(x, y, label='y_true')

    # compute linear predictions
    # x is a numpy array so each element gets mulitplied by slope and intercept is added
    y_pred = slope * x + intercept

    # plot the linear fit
    plt.plot(x, y_pred, color='black',
             ls=':',
             label='y_pred (regression)')

    # for each data point plot the error
    for idx, (x_i, y_i) in enumerate(zip(x, y)):
        # compute predicted position
        y_pred_i = slope * x_i + intercept

        # plot error
        plt.plot([x_i, x_i], [y_i, y_pred_i],
                 ls='--', lw=3, color='tab:red',
                 label='error' if idx == 0 else "")

    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')

    # # compute mean squared error
    # y_pred = slope * x + intercept

    # add title which shows model and MSE
    plt.suptitle(f'y_hat = {slope:.2f} * x + {intercept:.2f}, MSE = {mse:.3f}')
    plt.gcf().set_size_inches(10, 5)

def main():
    x = np.array([0, 1, 2, 3, 4, 5])
    y = np.array([1, 3.5, 4, 5, 4.5, 6])

    # reshape x to specify it is 1 feature and many samples
    x = x.reshape((-1, 1))

    # initialize sklearn model
    reg = LinearRegression()

    # fit the model
    reg.fit(x, y)

    # same as a_1
    slope = reg.coef_[0]

    # same as a_0
    intercept = reg.intercept_

    # show_fit is basically plotting it
    show_fit(x, y, slope, intercept)

    y_pred = reg.predict(x)

    r2 = r2_score(y_true=y, y_pred=y_pred)
    print(r2)


if __name__ == '__main__':
    main()