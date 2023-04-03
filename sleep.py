from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd


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


def avg_ds(ds, df_new):
    """
    Find the average across some range of deep sleep
    :param ds: (int) a user-selected range over which to find the rolling average
    :param df_new: (dataframe) a dataframe with a deep sleep percentage column
    :return: df_new: (dataframe) the dataframe updated with a Rolling Average column
    """
    # find the average deep sleep for each REM value in the selected range
    rem_range = [val for val in range(ds[0], ds[1])]
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

    # add the average line


    fig.add_scatter(x=)

    return fig


app.run_server(debug=True)