from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd


# read the csv files into dataframes
efficiency = pd.read_csv('data/Sleep_Efficiency.csv')
times = pd.read_csv('data/sleepdata_2.csv')
print(efficiency)
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


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide', 'value')
)
def update_sleep_corr(deepsleep):

    # filter out appropriate values
    cols = ['ID', 'Deep sleep percentage', 'REM sleep percentage']
    filt_deepsleep = filt_vals(efficiency, deepsleep, 'Deep sleep percentage', cols)

    # plot the data
    x = filt_deepsleep['Deep sleep percentage']
    y = filt_deepsleep['REM sleep percentage']

    fig = px.scatter(x, y, labels={'y': 'REM Sleep %',
                                   'x': 'Deep Sleep %'})

    return fig


app.run_server(debug=True)