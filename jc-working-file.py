from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
from datetime import datetime as dt


# read the csv files into dataframes
efficiency = pd.read_csv('Sleep_Efficiency.csv')
times = pd.read_csv('sleepdata.csv')
app = Dash(__name__)


# layout for the dashboard
app.layout = html.Div([
    html.H1("snoozless", style={'textAlign': 'center'}),

    # div for Deep Sleep v. REM Percentages
    html.Div([
        html.H2('Deep Sleep vs. REM Percentages', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-rem', style={'display': 'inline-block'}),

        # deep sleep slider
        html.P('Adjust Deep Sleep Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(15, 30, 1, value=[15,30], id='ds-slide')
    ]),

    # # div for Bedtime v. Wake Up Time
    # html.Div([
    #     html.H2('Bedtime vs. Wakeup Time', style={'textAlign': 'center'}),
    #     dcc.Graph(id='bd-wu', style={'display': 'inline-block'}),
    #
    #     # slider
    #     html.P('Adjust Hours Slept', style={'textAlign': 'left'}),
    #     dcc.RangeSlider(0, 30, 1, value=[1, 2], id='bd-slide')
    # ])


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



# USE PARSE TIME for sleep vs wakeup
# figure out filt_vals for the efficiency



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



# @app.callback(
#     Output('bd-wu', 'figure'),
#     Input('bd-slide', 'value')
# )
# def update_sleep_corr(bedtime):
#     bedtime = (get_time(bedtime[0]), get_time((bedtime[1])))
#
#     # convert datetime series to extract time
#     efficiency['Bedtime'] = get_time(efficiency['Bedtime'])
#     efficiency['Wakeup time '] = get_time(efficiency['Wakeup time'])
#
#     # filter out appropriate values
#     cols = ['ID', 'Bedtime', 'Wakeup time']
#     filt_bedtime = filt_vals(efficiency, bedtime, 'Bedtime', cols)
#
#     # convert Bedtime and Wakeup Time values to datetime
#     # dt.strptime(filt_bedtime['Bedtime'], "%Y-%m-%d %H:%M:%S")
#     # dt.strptime(filt_bedtime['Wakeup time'], "%Y-%m-%d %H:%M:%S")
#
#     # plot the data
#     x = filt_bedtime['Bedtime']
#     y = filt_bedtime['Wakeup time']
#
#     fig = px.scatter(x, y)
#
#     return fig

def avg_ds(ds, df_new):
    """
    Find the average across some range of deep sleep
    :param ds: (int) a user-selected range over which to find the rolling average
    :param df_new: (dataframe) a dataframe with a deep sleep percentage column
    :return: df_new: (dataframe) the dataframe updated with a Rolling Average column
    """

    # find the average deep sleep for each REM value in the selected range
    rem_range = [val for val in range(ds[0], ds[1] + 1)]

    # initialize a list
    avgs_list = []

    for i in rem_range:
        # make a new df for which the REM value is the same as i
        # avg that and append to list
        new_df = df_new[df_new['Deep sleep percentage'] == i]
        avg = new_df['REM sleep percentage'].mean()

        avgs_list.append(avg)

    # create a new column with the rolling average sunspots
    # df_new['Rolling Avg'] = df_new['Deep sleep percentage'].rolling(ds).mean()

    df_new.dropna(inplace=True)

    return rem_range, avgs_list


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide', 'value')
)
def update_sleep_corr(deepsleep):
    """
    Update the Deep Sleep vs. REM Sleep Percentage scatterplot
    based on user input
    :param deepsleep: (tuple) starting and ending values of deep sleep
        percentage to filter for
    :return: updated plot showing points only for slider-selected values
    """

    # filter out appropriate values
    cols = ['ID', 'Deep sleep percentage', 'REM sleep percentage']
    filt_deepsleep = filt_vals(efficiency, deepsleep, 'Deep sleep percentage', cols)

    # plot the data
    x = filt_deepsleep['Deep sleep percentage']
    y = filt_deepsleep['REM sleep percentage']

    fig = px.scatter(x, y, labels={'y': 'REM Sleep %',
                                   'x': 'Deep Sleep %'})

    rem_range, avgs_list = avg_ds(deepsleep, filt_deepsleep)

    fig.add_scatter(x=rem_range, y=avgs_list, name='Average Value')

    return fig

app.run_server(debug=True)