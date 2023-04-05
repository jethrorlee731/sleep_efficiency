from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime as dt


# read the csv files into dataframes
efficiency = pd.read_csv('data/Sleep_Efficiency.csv')

times = pd.read_csv('data/sleepdata.csv')
app = Dash(__name__)


# layout for the dashboard
app.layout = html.Div([
    html.H1("snoozless", style={'textAlign': 'center'}),
    #
    # # div for Deep Sleep v. REM Percentages
    # html.Div([
    #     html.H2('Deep Sleep vs. REM Percentages', style={'textAlign': 'center'}),
    #     dcc.Graph(id='ds-rem', style={'display': 'inline-block'}),
    #
    #     # deep sleep slider
    #     html.P('Adjust Deep Sleep Percentage', style={'textAlign': 'left'}),
    #     dcc.RangeSlider(15, 30, 1, value=[15,30], id='ds-slide')
    # ]),
    html.Div([
        html.P('Choose the dependent variable (sleep duration by default, including when invalid values are chosen)',
               style={'textAlign': 'center'}),

        # drop down menu to choose the value represented on the y-axis
        dcc.Dropdown(['Bedtime', 'Wakeup time', 'Sleep duration', 'Sleep efficiency', 'REM sleep percentage',
                      'Deep sleep percentage', 'Light sleep percentage', 'Awakenings', 'Caffeine consumption',
                      'Alcohol consumption', 'Exercise frequency'], value='Sleep duration', id='sleep-stat')
    ]),

    # div for Bedtime v. Other Stats
    html.Div([
        html.H2('Bedtime vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='bd-scatter', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-bd', inline=True
        ),

        # slider for bedtime
        html.P('Adjust Bedtime', style={'textAlign': 'left'}),
        dcc.RangeSlider(0, 23, 0.5, value=[0, 23], id='bd-slide'),
    ]),

    # div for Wakeup time v. Other Stats
    html.Div([
        html.H2('Wakeup Time vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='wu-scatter', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-wu', inline=True
        ),

        # slider for wakeup time
        html.P('Adjust Wakeup Time', style={'textAlign': 'left'}),
        dcc.RangeSlider(3, 12.5, 0.5, value=[3, 12.5], id='wu-slide'),
    ])


])


# filter out appropriate values
def filt_vals(df, vals, col, lcols):
    """
    Filter the user-selected values from the dataframe
    :param df: (dataframe) a dataframe with the values we are seeking and additional attributes
    :param vals: (list) two user-defined values, a min and max
    :param col: (str) the column to filter by
    :param lcols: (list) a list of column names to return
    :return: df_updated: (dataframe) the dataframe filtered to just include the values
            within the user specified range
    """
    least = vals[0]
    most = vals[1]

    df_update = df[df[col].between(least, most)][lcols]

    # return the updated dataframe to user
    return df_update


def parse_times(df_sleep, sleep_stat):
    """
    Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
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

    # # Parse no data if neither the bedtime or wakeup time columns are specified via the sleep_stat parameter
    # else:
    #     None
    return df_sleep


def _sleep_scatter(slider_values, show_trendline, sleep_stat_x, sleep_stat_y):
    """ Creates a scatter plot showing the relationship between two sleep statistics
    Args:
        slider_values (list of floats): a range of values for the independent variable to be represented on the plot
        show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
        sleep_stat_x (string): the independent variable of the scatter plot
        sleep_stat_y (string): the dependent variable of the scatter plot

    Returns:
        fig (px.scatter): the scatter plot itself
    """
    if sleep_stat_y in [None, sleep_stat_x]:
        sleep_stat_y = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', sleep_stat_x, sleep_stat_y]
    filt_deepsleep = filt_vals(efficiency, slider_values, sleep_stat_x, cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_deepsleep = parse_times(filt_deepsleep, sleep_stat_y)
    filt_deepsleep = parse_times(filt_deepsleep, sleep_stat_x)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_deepsleep, x=sleep_stat_x, y=sleep_stat_y, trendline=trendline,
                     labels={'x': sleep_stat_x, 'index': sleep_stat_y})

    return fig


filt_parsed = parse_times(efficiency, "Bedtime")
filt_parsed = parse_times(filt_parsed, "Wakeup time")

#BEDTIME
@app.callback(
    Output('bd-scatter', 'figure'),
    Input('bd-slide', 'value'),
    Input('scatter_trendline-bd', 'value'),
    Input('sleep-stat', 'value')
)
def update_bd_corr(bedtime, show_trendline, sleep_stat):

    # fig = _sleep_scatter(bedtime, show_trendline, "Bedtime", sleep_stat)
    if sleep_stat in [None, 'Bedtime']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Bedtime', sleep_stat]
    filt_deepsleep = filt_vals(filt_parsed, bedtime, 'Bedtime', cols)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_deepsleep, x="Bedtime", y=sleep_stat, trendline=trendline,
                     labels={'x': 'Bedtime', 'index': sleep_stat})

    return fig


@app.callback(
    Output('wu-scatter', 'figure'),
    Input('wu-slide', 'value'),
    Input('scatter_trendline-wu', 'value'),
    Input('sleep-stat', 'value')
)
def update_wu_corr(wakeuptime, show_trendline, sleep_stat):

    # fig = _sleep_scatter(bedtime, show_trendline, "Bedtime", sleep_stat)
    if sleep_stat in [None, 'Wakeup time']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Wakeup time', sleep_stat]
    filt_deepsleep = filt_vals(filt_parsed, wakeuptime, 'Wakeup time', cols)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_deepsleep, x="Wakeup time", y=sleep_stat, trendline=trendline,
                     labels={'x': 'Wakeup Time', 'index': sleep_stat})

    return fig


# @app.callback(
#     Output('ds-rem', 'figure'),
#     Input('ds-slide', 'value')
# )
# def update_sleep_corr(deepsleep):
#     """
#     Update the Deep Sleep vs. REM Sleep Percentage scatterplot
#     based on user input
#     :param deepsleep: (tuple) starting and ending values of deep sleep
#         percentage to filter for
#     :return: updated plot showing points only for slider-selected values
#     """
#
#     # filter out appropriate values
#     cols = ['ID', 'Deep sleep percentage', 'REM sleep percentage']
#     filt_deepsleep = filt_vals(efficiency, deepsleep, 'Deep sleep percentage', cols)
#
#     # plot the data
#     x = filt_deepsleep['Deep sleep percentage']
#     y = filt_deepsleep['REM sleep percentage']
#
#     fig = px.scatter(x, y, labels={'y': 'REM Sleep %',
#                                    'x': 'Deep Sleep %'})
#
#     rem_range, avgs_list = avg_ds(deepsleep, filt_deepsleep)
#
#     fig.add_scatter(x=rem_range, y=avgs_list, name='Average Value')
#
#     return fig

app.run_server(debug=True)

#
#
# from dash import Dash, html, dcc, Input, Output
# import plotly.express as px
# import pandas as pd
#
# # read the csv files into dataframes
# EFFICIENCY = pd.read_csv('data/Sleep_Efficiency.csv')
# TIMES = pd.read_csv('data/sleepdata_2.csv')
# app = Dash(__name__)
#
# # WE CAN EITHER MULTIPLY THE VALUES UP HERE OR ALTER THE COLUMN AFTER TAKING DEEP COPIES OF EFFICIENCY IN THE SCATTER
# # FUNCTIONS. WE CANNOT JUST ENTER THIS LINE IN OUR SCATTER PLOT FUNCTIONS FOR THE SLEEP EFFICIENCY VALUES WOULD MULTIPLY
#
# # multiply sleep efficiencies by 100 to represent them as percentages
# # EFFICIENCY['Sleep efficiency'] = EFFICIENCY['Sleep efficiency'] * 100
#
#
# # filter out appropriate values
# def filt_vals(df, vals, col, lcols):
#     """
#     Filter the user-selected values from the dataframe
#     Args:
#         df: (dataframe) a dataframe with the values we are seeking and additional attributes
#         vals (list): two user-defined values, a min and max
#         col (str): the column to filter by
#         lcols (list): a list of column names to return
#     Returns:
#         df_updated (dataframe): the dataframe filtered to just include the values within the user specified range
#     """
#     least = vals[0]
#     most = vals[1]
#
#     df_update = df[df[col].between(least, most)][lcols]
#
#     # return the updated dataframe to user
#     return df_update
#
#
# def parse_times(df_sleep, sleep_stat):
#     """
#     Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
#     Args:
#         df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
#         sleep_stat (str): The statistic to be portrayed on the box plot
#     Returns:
#         sleep_df (Pandas data frame): a newer version of the data frame with the parsed times
#     """
#     # parse the bedtime columns to only include hours into the day
#     if sleep_stat == 'Bedtime':
#         df_sleep['Bedtime'] = df_sleep['Bedtime'].str.split().str[1]
#         df_sleep['Bedtime'] = df_sleep['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / \
#                               60
#
#     # parse the wakeup time columns to only include hours into the day
#     elif sleep_stat == 'Wakeup time':
#         df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
#         df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
#                                   df_sleep['Wakeup time'].str[3:5].astype(float) / 60
#
#     # Parse no data if neither the bedtime or wakeup time columns are specified via the sleep_stat parameter
#     # else:
#     #     None
#
#     return df_sleep
#
#
# def _sleep_scatter(slider_values, show_trendline, sleep_stat_x, sleep_stat_y):
#     """ Creates a scatter plot showing the relationship between two sleep statistics
#     Args:
#         slider_values (list of floats): a range of values for the independent variable to be represented on the plot
#         show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
#         sleep_stat_x (string): the independent variable of the scatter plot
#         sleep_stat_y (string): the dependent variable of the scatter plot
#
#     Returns:
#         fig (px.scatter): the scatter plot itself
#     """
#     if sleep_stat_y in [None, sleep_stat_x]:
#         sleep_stat_y = 'Sleep duration'
#
#     trendline = None
#
#     # filter out appropriate values
#     cols = ['ID', sleep_stat_x, sleep_stat_y]
#     filt_deepsleep = filt_vals(EFFICIENCY, slider_values, sleep_stat_x, cols)
#
#     # change the times in the data frame to represent hours into a day as floats if they are getting plotted
#     filt_deepsleep = parse_times(filt_deepsleep, sleep_stat_y)
#
#     # show a trend line or not based on the user's input
#     if 'Show Trend Line' in show_trendline:
#         trendline = 'ols'
#
#     fig = px.scatter(filt_deepsleep, x=sleep_stat_x, y=sleep_stat_y, trendline=trendline,
#                      labels={'x': sleep_stat_x, 'index': sleep_stat_y})
#
#     return fig
#
# @app.callback(
#     Output('ds-sleep', 'figure'),
#     Input('ds-slide-sleep', 'value'),
#     Input('scatter_trendline-sleep', 'value'),
#     Input('sleep-stat', 'value')
# )
# def update_sleep_eff(sleepeff, show_trendline, sleep_stat):
#     """ Creates a scatter plot showing the relationship between sleep efficiency and another sleep statistic
#         Args:
#             sleepeff (list of floats): a range of sleep efficiencies to be represented on the plot
#             show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
#             sleep_stat (string): the dependent variable of the scatter plot
#
#         Returns:
#             fig (px.scatter): the sleep efficiency percentage vs. sleep statistic scatter plot itself
#     """
#     fig = _sleep_scatter(sleepeff, show_trendline, 'Sleep efficiency', sleep_stat)
#
#     return fig
# @app.callback(
#     Output('bd-wu', 'figure'),
#     Input('bd-slide', 'value'),
#     Input('wu-slide', 'value'),
#     Input('scatter_trendline-bdwu', 'value')
# )
# def update_sleep_corr(bedtime, wakeup, show_trendline):
#     """ Display the correlation between bedtime and wake time
#         Args:
#             bedtime (list): a list containing floats of the Bedtimes to display
#             wakeup (list): a list containing floats of the Wakeup times to display
#             show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
#
#         Returns:
#             fig (px.scatter): the bedtime vs. the wakeup times
#     """
#
#
# app.run_server(debug=True)
