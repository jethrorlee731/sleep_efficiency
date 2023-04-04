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

    # div for Bedtime v. Wake Up Time
    html.Div([
        html.H2('Bedtime vs. Wakeup Time', style={'textAlign': 'center'}),
        dcc.Graph(id='bd-wu', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-bdwu', inline=True
        ),

        # slider for bedtime
        html.P('Adjust Bedtime', style={'textAlign': 'left'}),
        dcc.RangeSlider(0, 23, 0.5, value=[0, 23], id='bd-slide'),

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

    # Parse no data if neither the bedtime or wakeup time columns are specified via the sleep_stat parameter
    else:
        None

# USE PARSE TIME for sleep vs wakeup
# parse bedtime and wakeup time from efficiency dataframe
parse_times(efficiency, "Bedtime")
parse_times(efficiency, 'Wakeup time')
# parse the bedtime and the wakeup time from df




# plot bedtime, wakeup time with sliders for each



# extract the time from a single value or series of datetime-formatted strings
# def get_time(datetime_val):
#     time_ser = []
#     if type(datetime_val) == int:
#         print(datetime_val)
#
#     else:
#         for val in datetime_val:
#             hms = val[11:]
#             # hms = dt.strptime(val, "%Y-%m-%d %H:%M:%S").time()
#             time_ser.append(hms)
#
#     return time_ser



@app.callback(
    Output('bd-wu', 'figure'),
    Input('bd-slide', 'value'),
    Input('wu-slide', 'value'),
    Input('scatter_trendline-bdwu', 'value')
)
def update_sleep_corr(bedtime, wakeup, show_trendline):
    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Bedtime', 'Wakeup time']

    filt_bedtime = filt_vals(efficiency, bedtime, 'Bedtime', cols)
    filt_both = filt_vals(filt_bedtime, wakeup, 'Wakeup time', cols)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    # plot the data
    fig = px.scatter(filt_both, x='Bedtime', y='Wakeup time', trendline=trendline)

    return fig

#
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