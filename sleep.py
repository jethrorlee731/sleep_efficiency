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
        html.P('Choose the dependent variable (sleep duration by default, including when invalid values are chosen)',
                style={'textAlign': 'center'}),

        # drop down menu to choose the value represented on the y-axis
        dcc.Dropdown(['Bedtime', 'Wakeup time', 'Sleep duration', 'Sleep efficiency', 'REM sleep percentage',
                      'Deep sleep percentage', 'Light sleep percentage', 'Awakenings', 'Caffeine consumption',
                      'Alcohol consumption', 'Exercise frequency'], value='Sleep duration', id='sleep-stat')
    ]),

    # div for Deep Sleep Percentage vs. other variables
    html.Div([
        html.H2('Deep Sleep Percentage vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-deep', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-deep', inline=True
        ),

        # deep sleep slider
        html.P('Adjust Deep Sleep Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(15, 30, 1, value=[15, 30], id='ds-slide-deep')]),
    # div for REM Sleep Percentage vs. other variables
    html.Div([
        html.H2('REM Sleep Percentage vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-rem', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-rem', inline=True
        ),

        # deep sleep slider
        html.P('Adjust REM Sleep Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(15, 30, 1, value=[15, 30], id='ds-slide-rem')]),
    # div for Sleep Efficiency vs. other variables
    html.Div([
        html.H2('Sleep Efficiency vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-sleep', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-sleep', inline=True
        ),

        # deep sleep slider
        html.P('Adjust Sleep Efficiency Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(15, 30, 1, value=[15, 30], id='ds-slide-sleep')]),

    # div for Box Plot Distributions by Gender
    html.Div([
        html.H2('Distribution by Gender', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-gender', style={'display': 'inline-block'}),

        # gender checkbox
        dcc.Checklist(
            ['Male', 'Female'],
            ['Male', 'Female'], id='ds-gender-options', inline=True
        )]),

    # div for calculating sleep score
    html.Div([
        html.H2('Find your sleep score!', style={'textAlign': 'center'}),
        # dcc.Graph(id='ds-gender', style={'display': 'inline-block'}),

        # Ask user for information that could affect their sleep efficiency

        # Ask for a user's age
        html.P('How old are you? (years)', style={'textAlign': 'center'}),
        dcc.Slider(0, 120, 1, value=0, marks=None, id='sleep-score-age',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user how many drinks of alcohol they consume, on average, per week
        html.P('How many drinks of alcohol do you typically drink in a week?',
               style={'textAlign': 'center'}),
        html.P('Standard drinks:', style={'textAlign': 'center'}),
        html.P('- 12 ounces of 5% alcohol by volume (ABV) like beer', style={'textAlign': 'center'}),
        html.P('- 8 ounces of 7% ABV like malt liquor', style={'textAlign': 'center'}),
        html.P('- 5 ounces of 12% ABV like wine', style={'textAlign': 'center'}),
        html.P('- 1.5 ounces of 40% ABV (or 80 proof) distilled spirits like gin, rum and whiskey',
               style={'textAlign': 'center'}),
        dcc.Slider(0, 50, 1, value=0, marks=None, id='sleep-score-alcohol',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user about their exercise habits per week
        html.P('How many hours of physical activity do you get in a week', style={'textAlign': 'center'}),
        dcc.Slider(0, 168, 1, value=0, marks=None, id='sleep-score-exercise',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user about whether or not they smoke/vape
        html.P('Do you smoke/vape?', style={'textAlign': 'center'}),
        dcc.Dropdown(['Yes', 'No'], clearable=False, id='sleep-score-smoke'),

        # Ask a user about how many hours of sleep they get, on average, per day
        html.P('On average, how many hours do you sleep in a day?', style={'textAlign': 'center'}),
        dcc.Slider(0, 24, 1, value=0, marks=None, id='sleep-score-duration',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user how many cups of caffeine they consume per week
        html.P('On average, how many cups of caffeine do you consume per week?', style={'textAlign': 'center'}),
        dcc.Slider(0, 100, 1, value=0, marks=None, id='sleep-score-caffeine',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user for they gender they identify with
        html.P("What's your gender identity?", style={'textAlign': 'center'}),
        dcc.Dropdown(['Male', 'Female', 'Non-binary'], clearable=False, id='sleep-score-gender'),

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
    Output('ds-deep', 'figure'),
    Input('ds-slide-deep', 'value'),
    Input('scatter_trendline-deep', 'value'),
    Input('sleep-stat', 'value')
)
def update_deep_sleep(deepsleep, show_trendline, sleep_stat):

    if sleep_stat in [None, 'Deep sleep percentage']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Deep sleep percentage', sleep_stat]
    filt_deepsleep = filt_vals(EFFICIENCY, deepsleep, 'Deep sleep percentage', cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_deepsleep = parse_times(filt_deepsleep, sleep_stat)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_deepsleep, x='Deep sleep percentage', y=sleep_stat, trendline=trendline,
                     labels={'x': 'Deep Sleep %', 'index': sleep_stat})

    return fig

@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide-rem', 'value'),
    Input('scatter_trendline-rem', 'value'),
    Input('sleep-stat', 'value')
)
def update_rem_sleep(remsleep, show_trendline, sleep_stat):

    if sleep_stat in [None, 'REM sleep percentage']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'REM sleep percentage', sleep_stat]
    filt_remsleep = filt_vals(EFFICIENCY, remsleep, 'REM sleep percentage', cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_remsleep = parse_times(filt_remsleep, sleep_stat)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_remsleep, x='REM sleep percentage', y=sleep_stat, trendline=trendline,
                     labels={'x': 'REM Sleep %', 'index': sleep_stat})

    return fig

@app.callback(
    Output('ds-sleep', 'figure'),
    Input('ds-slide-sleep', 'value'),
    Input('scatter_trendline-sleep', 'value'),
    Input('sleep-stat', 'value')
)
def update_sleep_eff(sleepeff, show_trendline, sleep_stat):

    if sleep_stat in [None, 'Sleep efficiency']:
        sleep_stat = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Sleep efficiency', sleep_stat]
    filt_sleepeff = filt_vals(EFFICIENCY, sleepeff, 'Sleep efficiency', cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_sleepeff = parse_times(filt_sleepeff, sleep_stat)

    filt_sleepeff['Sleep efficiency'] = filt_sleepeff['Sleep efficiency'] * 100

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_sleepeff, x='Sleep efficiency', y=sleep_stat, trendline=trendline,
                     labels={'x': 'Sleep Efficiency %', 'index': sleep_stat})
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
