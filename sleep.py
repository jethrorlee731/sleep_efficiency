from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import statsmodels

# read the csv files into dataframes
EFFICIENCY = pd.read_csv('data/Sleep_Efficiency.csv')
TIMES = pd.read_csv('data/sleepdata_2.csv')
app = Dash(__name__)

# layout for the dashboard
app.layout = html.Div([
    html.H1("snoozless", style={'textAlign': 'center'}),

    # div for Deep Sleep v. REM Percentages
    html.Div([
        html.H2('Deep Sleep vs. REM Percentages', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-rem', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline', inline=True
        ),

        # deep sleep slider
        html.P('Adjust Deep Sleep Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(15, 30, 1, value=[15, 30], id='ds-slide')
    ]),

    # div for Deep Sleep Box Plot Distributions by Gender
    html.Div([
        html.H2('Deep Sleep Distribution by Gender', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-gender', style={'display': 'inline-block'}),

        # gender checkbox
        dcc.Checklist(
            ['Male', 'Female'],
            ['Male', 'Female'], id='ds-gender-options', inline=True
        ),

        # dropdown menu to choose the data represented on the chart(s?)
        dcc.Dropdown(['Bedtime', 'Wakeup time', 'Sleep duration', 'Sleep efficiency', 'REM sleep percentage',
                      'Deep sleep percentage', 'Light sleep percentage', 'Awakenings', 'Caffeine consumption',
                      'Alcohol consumption', 'Exercise frequency'], 'Deep sleep percentage',
                     id='sleep-stat', clearable=False),

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
    Input('ds-slide', 'value'),
    Input('scatter_trendline', 'value')
)
def update_sleep_corr(deepsleep, show_trendline):
    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Deep sleep percentage', 'REM sleep percentage']
    filt_deepsleep = filt_vals(EFFICIENCY, deepsleep, 'Deep sleep percentage', cols)

    # plot the data
    x = filt_deepsleep['Deep sleep percentage']
    y = filt_deepsleep['REM sleep percentage']
   
    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(x, y, trendline=trendline, labels={'y': 'REM Sleep %',
                                                    'x': 'Deep Sleep %'})

    return fig


@app.callback(
    Output('ds-gender', 'figure'),
    Input('ds-gender-options', 'value'),
    Input('sleep-stat', 'value')
)
def show_sleep_gender_stats(genders, sleep_stat):
    """
    Shows box plots that represents distributions of a sleep statistic per gender
    Args:
        genders (list of str): list of genders to be shown on the box and whisker chart
        sleep_stat (str): The statistic to be portrayed on the box plot
    Returns:
        fig: the box and whisker chart
    """
    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY.loc[EFFICIENCY.Gender.isin(genders),]

    # plot the box and whisker chart
    fig = px.box(sleep_gender, x='Gender', y=sleep_stat, color='Gender', color_discrete_sequence=['fuchsia', 'orange'])

    return fig


app.run_server(debug=True)
