from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# read the csv files into dataframes
EFFICIENCY = pd.read_csv('data/Sleep_Efficiency.csv')
TIMES = pd.read_csv('data/sleepdata_2.csv')
app = Dash(__name__)

# layout for the dashboard
# WE CAN DECIDE ON THE FORMAT OF THE LAYOUT LATER AND USE CHILDRENS TO REFORMAT
app.layout = html.Div([
    html.H1("snoozless", style={'textAlign': 'center'}),

    # div for drop down filter for scatter and box plots
    html.Div([
        html.H2('Choose the dependent variable (sleep duration by default, including when invalid values are chosen)',
                style={'textAlign': 'center'}),

        # drop down menu to choose the value represented on the y-axis
        dcc.Dropdown(['Bedtime', 'Wakeup time', 'Sleep duration', 'Sleep efficiency', 'REM sleep percentage',
                      'Deep sleep percentage', 'Light sleep percentage', 'Awakenings', 'Caffeine consumption',
                      'Alcohol consumption', 'Exercise frequency'], value='Sleep duration',
                     id='sleep-stat')
    ]),

    # div for Deep Sleep vs. other variables
    html.Div([
        html.H2('Deep Sleep vs. Sleep Statistics', style={'textAlign': 'center'}),
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

    # div for Box Plot Distributions by Gender
    html.Div([
        html.H2('Distribution by Gender', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-gender', style={'display': 'inline-block'}),

        # gender checkbox
        dcc.Checklist(
            ['Male', 'Female'],
            ['Male', 'Female'], id='ds-gender-options', inline=True
        ),

    ])

])


# filter out appropriate values
def filt_vals(df, vals, col, lcols):
    """
    Filter the user-selected values from the dataframe
    Args:
        df: (dataframe) a dataframe with the values we are seeking and additional attributes
        vals (list): two user-defined values, a min and max
        col (str): the column to filter by
        lcols (list): a list of column names to return
    Returns:
        df_updated (dataframe): the dataframe filtered to just include the values within the user specified range
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

    return df_sleep


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide', 'value'),
    Input('scatter_trendline', 'value'),
    Input('sleep-stat', 'value')
)
def update_sleep_corr(deepsleep, show_trendline, sleep_stat):

    # DS-SLIDE IS NOT INCLUDED IN THIS FUNCTION YET?

    if sleep_stat in [None, 'Deep sleep percentage']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Deep sleep percentage', sleep_stat]
    filt_deepsleep = filt_vals(EFFICIENCY, deepsleep, 'Deep sleep percentage', cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_deepsleep = parse_times(filt_deepsleep, sleep_stat)

    # plot the data
    x = filt_deepsleep['Deep sleep percentage']
    y = filt_deepsleep[sleep_stat]

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(x, y, trendline=trendline, labels={'x': 'Deep Sleep %', 'index': sleep_stat})

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
    if sleep_stat in [None, 'Deep sleep percentage']:
        sleep_stat = 'Sleep duration'

    ylabel = sleep_stat

    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY.loc[EFFICIENCY.Gender.isin(genders),]

    # plot the box and whisker chart
    fig = px.box(sleep_gender, x='Gender', y=sleep_stat, color='Gender',
                 color_discrete_map={'Female': 'fuchsia', 'Male': 'orange'}, labels={sleep_stat: ylabel})

    return fig


app.run_server(debug=True)
