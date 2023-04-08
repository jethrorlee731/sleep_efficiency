from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# read the csv files into dataframes
efficiency = pd.read_csv('data/Sleep_Efficiency.csv')
EFFICIENCY = efficiency.copy()
EFFICIENCY = EFFICIENCY.dropna()
TIMES = pd.read_csv('data/sleepdata_2.csv')

app = Dash(__name__)

# multiply sleep efficiencies by 100 to represent them as percentages
EFFICIENCY.loc[:, 'Sleep efficiency'] = EFFICIENCY['Sleep efficiency'] * 100

# clarifying metrics
EFFICIENCY = EFFICIENCY.rename(columns={'Exercise frequency': 'Exercise frequency (in days per week)'})


def _parse_times(df_sleep):
    """ Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
    Returns:
        df_sleep (Pandas data frame): a newer version of the data frame with the parsed times
    """
    # parse the bedtime columns to only include hours into the day (military time)
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str.split().str[1]
    df_sleep['Bedtime'] = df_sleep['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / 60

    # parse the wakeup time columns to only include hours into the day (military time)
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
    df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
                              df_sleep['Wakeup time'].str[3:5].astype(float) / 60
    return df_sleep


EFFICIENCY = _parse_times(EFFICIENCY)

# layout for the dashboard
# WE CAN DECIDE ON THE FORMAT OF THE LAYOUT LATER AND USE CHILDRENS TO REFORMAT

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Sleep Statistics', children=[
            html.Div([
                html.Div([
                    html.H1("snoozeless", style={'textAlign': 'center', 'font-family': 'Cursive'}),

                    # Define what "sleep efficiency" actually means
                    html.P('"Sleep efficiency" refers to the ratio of time that one rests in bed while actually '
                           'asleep'),

                    # Explain the importance of sleep efficiency, REM sleep percentage, and deep sleep percentage
                    html.P('Allowing people to sleep the most efficiently is essential as the amount of rest we get '
                           'impacts our health and well-being every day. As college students, sleep is even more '
                           'precious and limited. We are all very interested in learning how to make the most of our '
                           'limited sleep times. Aside from us, people that fall into other demographic groups would '
                           'benefit from understanding what factors help to maximize REM sleep percentages or deep '
                           'sleep percentages. Sleep is a necessity, so it would be difficult for one to not be '
                           'interested in learning more about how to better their sleep through methods such as '
                           'maximizing the time they are in the deep sleep stage. '),
                    html.P("REM sleep is responsible for helping people process new knowledge and execute motor "
                           "skills to their fullest potential. Deep sleep enables the body to release vital growth "
                           "hormones that work to build muscles, tissues, and bones")
                ], style={'background-color': 'blue', 'color': 'white'}
                ),

                # div for drop down filter for all the plots except the machine learning models, strip chart,
                # and deep contour plot
                dbc.Row([
                    html.Div([
                        html.P('Choose the dependent variable.',
                               style={'textAlign': 'center'}),

                        # drop down menu to choose the value represented on the y-axis
                        dcc.Dropdown(
                            ['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                             'Light sleep percentage', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                             'Exercise frequency (in days per week)', 'Age', 'Wakeup time', 'Bedtime'],
                            value='Sleep duration', id='sleep-stat-dep', style={'background-color': 'royalblue',
                                                                                'color': 'black'})
                    ], style={'background-color': 'midnightblue', 'color': 'white'}
                    )
                ]),

                # div containing the scatter plot and gender distribution plots
                # div for a scatter plot comparing the relationship between two sleep variables
                dbc.Row([
                    html.Div([
                        html.Div([
                            html.H2('How Certain Factors Affect Your Sleep Quality', style={'textAlign': 'center'}),
                            dcc.Graph(id='sleep-scatter',
                                      style={'display': 'inline-block', 'width': '45vw', 'height': '45vh'}),

                            html.P('Select an independent variable you are interested in observing.'),
                            dcc.Dropdown(
                                ['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                                 'Exercise frequency (in days per week)', 'Age', 'Wakeup time', 'Bedtime'],
                                value='Age', clearable=False, id='sleep-stat-ind', style={'display': 'inline-block',
                                                                                          'width': '100%',
                                                                                          'background-color':
                                                                                              'royalblue',
                                                                                          'color': 'black'}),

                            # Add instructors that tell users how to control how much data gets represented
                            html.P('Adjust the axes values by brushing over points you want to inspect more closely',
                                   style={'textAlign': 'left'}),

                            # checkbox to toggle trend-line
                            dcc.Checklist(
                                ['Show Trend Line'],
                                ['Show Trend Line'], id='scatter-trend-line', inline=True,
                                style={'background-color': 'midnightblue'}
                            ),
                        ],
                            # Add style parameters to this Div, placing it in the left 49% of the page
                            style={'width': '49%', 'display': 'inline-block', 'float': 'left',
                                   'background-color': 'midnightblue'}),

                        # div for comparing sleep statistic distributions between genders
                        html.Div([
                            html.H2('Sleep Statistics Across Genders', style={'textAlign': 'center'}),
                            # div for violin plot distributions of a sleep statistic by gender
                            html.Div([
                                dcc.Graph(id='violin-gender',
                                          style={'display': 'inline-block', 'width': '49%', 'float': 'left'})
                            ]),

                            # div for histogram distribution of a sleep statistic by gender (uses the same checkbox as
                            # the violin plot)
                            html.Div([
                                dcc.Graph(id='hist-gender', style={'display': 'inline-block', 'width': '49%'})
                            ]),
                            # gender checkbox
                            html.P('Filter the plots by gender', style={'textAlign': 'center'}),
                            dcc.Checklist(
                                ['Male', 'Female'],
                                ['Male', 'Female'], id='gender-options', inline=True, style={'textAlign': 'center'}
                            )
                        ],
                            # Add style parameters to this Div
                            style={'width': '49%', 'display': 'inline-block', 'height': '80vh'}),
                    ], id='scatter-and-gender', style={'background-color': 'midnightblue', 'color': 'white'}
                    )]),

                # div for strip and density plots
                dbc.Row([
                    html.Div([
                        # a slider that allows users to adjust the range of sleep efficiency values on the strip and
                        # contour plots
                        html.Div([
                            html.P('Adjust the sleep efficiency percentages presented on the two plots below',
                                   style={'textAlign': 'left'}),
                            dcc.RangeSlider(50, 100, 1, value=[50, 100], id='efficiency-slider',
                                            tooltip={"placement": "bottom", "always_visible": True}, marks=None)
                        ], style={'background-color': 'indigo'}
                        ),

                        # div for smoking status strip chart
                        html.Div([
                            # creating a strip chart showing the relationship between one's smoking status and a sleep
                            # variable
                            html.H2('How Smoking Affects Your Sleep Quality', style={'textAlign': 'center'}),
                            dcc.Graph(id='smoke-vs-sleep', style={'display': 'inline-block'}),

                            # specify to the users how they can filter the data by smoking status
                            html.P(
                                "Filter by smoking status in the strip chart by clicking in the legend on the smoking "
                                "status that you do not want to focus on."),
                        ],
                            # Add style parameters to this Div
                            style={'width': '50%', 'display': 'inline-block', 'float': 'left',
                                   'background-color': 'indigo', 'height': '48vw'}),

                        # div for density contour plot (comparing a combination of variables with sleep efficiency)
                        html.Div([
                            html.H2('How Various Features Affect Sleep Efficiency', style={'textAlign': 'center'}),
                            dcc.Graph(id='efficiency-contour', style={'display': 'inline-block', 'height': '45vh'}),

                            html.P(
                                'Choose one independent variable to be represented in the density contour plot (sleep '
                                'duration by default, including when invalid values are chosen)',
                                style={'textAlign': 'center'}),

                            # drop down menu to choose the first independent variable for the density contour plot
                            dcc.Dropdown(
                                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage',
                                 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                                 'Exercise frequency (in days per week)',
                                 'Age',
                                 'Wakeup time', 'Bedtime', 'Gender', 'Smoking status'],
                                value='Sleep duration', id='density-stat1',
                                style={'background-color': 'mediumslateblue',
                                       'color': 'black'}),

                            html.P(
                                'Choose the another variable to be represented in the density contour plot (light '
                                'sleep percentage by default, including when invalid values are chosen)',
                                style={'textAlign': 'center'}),

                            # drop down menu to choose the second independent variable for the density contour plot
                            dcc.Dropdown(
                                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage',
                                 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                                 'Exercise frequency (in days per week)',
                                 'Age',
                                 'Wakeup time', 'Bedtime', 'Gender', 'Smoking status'],
                                value='Light sleep percentage', id='density-stat2',
                                style={'background-color': 'mediumslateblue', 'color': 'black'})
                        ],
                            # Add style parameters to this Div
                            style={'width': '50%', 'display': 'inline-block', 'float': 'right',
                                   'background-color': 'indigo', 'height': '48vw'})]),

                    # div for the two graphs created by a random forest regressor and multiple regression model +
                    # sleep hygiene plot
                    dbc.Row([
                        html.Div([

                            # div for the feature importance bar chart
                            html.Div([
                                html.H2('Which variables are most important in determining sleep efficiency, '
                                        'REM sleep percentage, or deep sleep percentage?',
                                        style={'textAlign': 'center'}),
                                html.P('Indicate the dependent variable you are interested in looking at.'),
                                dcc.Dropdown(['Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage'],
                                             value='Sleep efficiency',
                                             clearable=False, id='feature', style={'background-color': 'mediumpurple',
                                                                                   'color': 'black'}),
                                dcc.Graph(id="feature-importance",
                                          style={'display': 'inline-block', 'width': '100%', 'height': '60%'})
                            ],
                                # Add style parameters to this Div
                                style={'width': '25%', 'display': 'inline-block', 'float': 'left',
                                       'background-color': 'darkviolet', 'height': '51vw'}),

                            # div for radar graph of sleep hygiene
                            html.Div([
                                html.H2('Sleep Hygiene', style={'textAlign': 'center'}),

                                # allows the user to control the variables displayed on the graph
                                dcc.Dropdown(
                                    ['Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                                     'Exercise frequency (in days per week)'],
                                    id='radar-features', style={'background-color': 'white', 'color': 'black'},
                                    multi=True,
                                    value=['Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                                           'Exercise frequency (in days per week)'],
                                ),

                                # plots the radar graph on the dashboard
                                dcc.Graph(id="sleep-hygiene", style={'display': 'inline-block', 'width': '100%'})
                            ],
                                # Add style parameters to this Div
                                style={'width': '25%', 'display': 'inline-block', 'float': 'left',
                                       'background-color': 'darkviolet', 'height': '51vw'}
                            ),

                            # div for a 3D scatter plot showing relationship between 2 independent sleep variables
                            # and 1 dependent sleep variable
                            html.Div([
                                html.H2('3D view of two independent variables against a chosen dependent variable',
                                        style={'textAlign': 'center'}),
                                html.P('Select three independent variables you are interested in looking at.'),
                                dcc.Dropdown(
                                    ['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption',
                                     'Alcohol consumption',
                                     'Exercise frequency (in days per week)', 'Age', 'Wakeup time', 'Bedtime',
                                     'Smoking status'],
                                    value='Age', clearable=False, id='independent-3D-feat1',
                                    style={'background-color': 'mediumpurple', 'color': 'black'}),
                                dcc.Dropdown(
                                    ['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption',
                                     'Alcohol consumption',
                                     'Exercise frequency (in days per week)', 'Age', 'Wakeup time', 'Bedtime',
                                     'Smoking status'],
                                    value='Awakenings', clearable=False, id='independent-3D-feat2',
                                    style={'background-color': 'mediumpurple', 'color': 'black'}),
                                html.P('Select dependent variable you are interested in looking at.'),
                                dcc.Dropdown(['Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage'],
                                             value='Sleep efficiency',
                                             clearable=False, id='dependent-feature',
                                             style={'background-color': 'mediumpurple', 'color': 'black'}),
                                html.P(
                                    'Filter by gender in the 3D scatter by clicking in the legend on the gender '
                                    'that you do not want to focus on.'),
                                dcc.Graph(id="three-dim-plot", style={'display': 'inline-block'})
                            ],
                                # Add style parameters to this Div
                                style={'width': '50%', 'display': 'inline-block', 'float': 'right',
                                       'background-color': 'darkviolet', 'height': '51vw'}
                            ),
                        ])
                    ])
                ]),
            ], style={'background-color': 'midnightblue', 'color': 'white'})
        ], style={'background-color': 'black', 'color': 'white'}),

        dcc.Tab(label='Sleep Quality Predictor', children=[
            # div for machine learning components
            html.Div([
                # div for calculating sleep efficiency, REM sleep percentage, and Deep sleep percentage
                # based on the multiple learning regression model
                html.Div([
                    html.H2('Find your sleep efficiency, REM sleep percentage, and deep sleep percentage!',
                            style={'textAlign': 'center'}),

                    # Ask user information that are going to be inputs into the multiple learning regression model
                    # Div for sliders
                    dbc.Col([
                        html.Div([
                            # Ask a user for their age
                            html.Div([
                                html.P('How old are you?', style={'textAlign': 'center'}),
                                dcc.Slider(0, 100, 1, value=15, marks=None, id='sleep-age',
                                           tooltip={"placement": "bottom", "always_visible": True})]),

                            # Ask a user what is their bedtime (hours into the day)
                            html.Div([
                                html.P('What is your bedtime based on hours into the day (military time)?',
                                       style={'textAlign': 'center'}),
                                dcc.Slider(0, 24, 0.25, value=23, marks=None, id='sleep-bedtime',
                                           tooltip={'placement': 'bottom', 'always_visible': True})]),

                            # Ask a user what is their wakeup time (hours into the day)
                            html.Div([
                                html.P('What is your wakeup time based on hours into the day (military time)?',
                                       style={'textAlign': 'center'}),
                                dcc.Slider(0, 24, 0.25, value=9, marks=None, id='sleep-wakeuptime',
                                           tooltip={'placement': 'bottom', 'always_visible': True})]),

                            # Ask a user how long they sleep for (wakeup time minus bedtime)
                            html.Div([
                                html.P('What is the total amount of time you slept (in hours)?',
                                       style={'textAlign': 'center'}),
                                dcc.Slider(0, 15, 0.25, value=7, marks=None, id='sleep-duration',
                                           tooltip={'placement': 'bottom', 'always_visible': True})]),

                            # Ask a user the amount of caffeine consumption in the 24 hours prior to bedtime (in mg)
                            html.Div([
                                html.P(
                                    'What is your amount of caffeine consumption in the 24 hours prior to bedtime '
                                    '(in mg)?',
                                    style={'textAlign': 'center'}), dcc.Slider(0, 200, 1, value=50,
                                                                               marks=None, id='sleep-caffeine',
                                                                               tooltip={'placement': 'bottom',
                                                                                        'always_visible': True})])
                        ],
                            style={'width': '50%', 'float': 'left', 'height': '35vw'})]),

                    # Div for drop down menus
                    dbc.Col([
                        html.Div([
                            # Ask a user for their biological gender
                            html.Div([
                                html.P("What's your biological gender?", style={'textAlign': 'center'}),
                                dcc.Dropdown(['Biological Male', 'Biological Female'], value='Biological Male',
                                             clearable=False, id='sleep-gender',
                                             style={'margin': 'auto', 'width': '70%',
                                                    'color': 'black'})]),

                            # Ask a user the number of awakenings they have for a given night
                            html.Div([
                                html.P('What is the number of awakenings you have for a given night?',
                                       style={'textAlign': 'center'}),
                                dcc.Dropdown([0, 1, 2, 3, 4], value=0, clearable=False, id='sleep-awakenings',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user the amount of alcohol consumption in the 24 hours prior to bedtime (in oz)
                            html.Div([
                                html.P(
                                    'What is your amount of alcohol consumption in the 24 hours prior to bedtime (in '
                                    'oz)?',
                                    style={'textAlign': 'center'}),
                                dcc.Dropdown([0, 1, 2, 3, 4, 5], value=0, clearable=False,
                                             id='sleep-alcohol',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user about whether they smoke/vape
                            html.Div([
                                html.P('Do you smoke/vape?', style={'textAlign': 'center'}),
                                dcc.Dropdown(['Yes', 'No'], value='No', clearable=False, id='sleep-smoke',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user the number of times the test subject exercises per week
                            html.Div([
                                html.P('How many times do you exercise per week?', style={'textAlign': 'center'}),
                                dcc.Dropdown([0, 1, 2, 3, 4, 5], value=2, clearable=False, id='sleep-exercise',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})])
                        ], style={'width': '50%', 'float': 'right', 'height': '35vw'})]),

                    dbc.Row([
                        html.H2(id='sleep-eff', style={'textAlign': 'center'}),
                        html.H2(id='sleep-rem', style={'textAlign': 'center'}),
                        html.H2(id='sleep-deep', style={'textAlign': 'center'})])
                ])
            ], style={'background-color': 'darkslateblue', 'color': 'white'})
        ], style={'background-color': 'black', 'color': 'white'})
    ])
], style={'font-family': 'Courier New'})


def filt_vals(df, vals, col, lcols):
    """ Filter the user-selected values from the dataframe
    Args:
        df: (dataframe) a dataframe with the values we are seeking and additional attributes
        vals (list): two user-defined values, a min and max
        col (str): the column to filter by
        lcols (list): a list of column names to return
    Returns:
        df_updated (dataframe): the dataframe filtered to just include the values within the user specified range
    """
    # identify the beginning and end of the range
    least = vals[0]
    most = vals[1]

    # filter out the rows for which the column values are within the range
    df_update = df[df[col].between(least, most)][lcols]

    # return the updated dataframe to user
    return df_update


@app.callback(
    Output('sleep-scatter', 'figure'),
    Input('scatter-trend-line', 'value'),
    Input('sleep-stat-ind', 'value'),
    Input('sleep-stat-dep', 'value')
)
def make_sleep_scatter(show_trend_line, sleep_stat_ind, sleep_stat_dep):
    """ Creates a scatter plot showing the relationship between two sleep statistics
    Args:
        show_trend_line (string): a string indicating whether a trend line should appear on the scatter plot
        sleep_stat_ind (string): the independent variable of the scatter plot
        sleep_stat_dep (string): the dependent variable of the scatter plot

    Returns:
        fig (px.scatter): the scatter plot itself
    """
    df_sleep = EFFICIENCY

    if sleep_stat_ind == 'Gender' or sleep_stat_dep == 'Gender':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Gender_Male': 'Gender'})

    if sleep_stat_ind == 'Smoking status' or sleep_stat_dep == 'Smoking status':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Smoking status'], drop_first=True)
        df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    # initialize the trend-line as None
    trend_line = None

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trend_line:
        trend_line = 'ols'

    # plot the sleep statistic (x) and the other sleep statistic (y)
    fig = px.scatter(EFFICIENCY, x=sleep_stat_ind, y=sleep_stat_dep, trendline=trend_line, template='plotly_dark',
                     labels={'x': sleep_stat_ind, 'index': sleep_stat_dep})

    return fig


@app.callback(
    Output('violin-gender', 'figure'),
    Input('gender-options', 'value'),
    Input('sleep-stat-dep', 'value')
)
def show_sleep_gender_violin_plot(genders, sleep_stat):
    """ Shows violin plots that represents distributions of a sleep statistic per gender
    Args:
        genders (list of str): list of genders to be shown on the violin plot
        sleep_stat (str): The statistic to be portrayed on the violin plot
    Returns:
        fig: the violin plot
    """
    df_sleep = EFFICIENCY

    if sleep_stat == 'Smoking status':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Smoking status'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    # filter the data based on the chosen genders
    sleep_gender = df_sleep.loc[df_sleep.Gender.isin(genders),]

    # plot the violin chart
    fig = px.violin(sleep_gender, x='Gender', y=sleep_stat, color='Gender', template='plotly_dark',
                    color_discrete_map={'Female': 'sienna', 'Male': 'blue'})

    return fig


@app.callback(
    Output('hist-gender', 'figure'),
    Input('gender-options', 'value'),
    Input('sleep-stat-dep', 'value')
)
def show_sleep_gender_histogram(genders, sleep_stat):
    """ Shows a histogram that represents distributions of a sleep statistic per gender
    Args:
        genders (list of str): list of genders to be shown on the histogram
        sleep_stat (str): The statistic to be portrayed on the histogram
    Returns:
        fig: the histogram itself
    """
    df_sleep = EFFICIENCY

    if sleep_stat == 'Smoking status':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Smoking status'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    # filter the data based on the chosen genders
    sleep_gender = df_sleep.loc[df_sleep.Gender.isin(genders),]

    # plot the histogram
    # show multiple histograms color coded by biological gender if both the "male" and "female" checkboxes are ticked
    fig = px.histogram(sleep_gender, x=sleep_stat, color='Gender', template='plotly_dark',
                       color_discrete_map={'Female': 'sienna', 'Male': 'blue'})

    return fig


@app.callback(
    Output('efficiency-contour', 'figure'),
    Input('density-stat1', 'value'),
    Input('density-stat2', 'value'),
    Input('efficiency-slider', 'value')
)
def show_efficiency_contour(sleep_stat1, sleep_stat2, slider_values):
    """ Shows a density contour plot that plots the relationship between two variables and average sleep efficiency
    Args:
        sleep_stat1 (str): One statistic to be portrayed on the density contour plot
        sleep_stat2 (str): Another statistic to be portrayed on the density contour plot
        slider_values (list of floats): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the density contour plot
    """
    df_sleep = EFFICIENCY

    if sleep_stat1 == 'Gender' or sleep_stat2 == 'Gender':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Gender'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Gender_Male': 'Gender'})

    if sleep_stat1 == 'Smoking status' or sleep_stat2 == 'Smoking status':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Smoking status'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    # assign a variable name to the string "Sleep efficiency"
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    # check whether the sleep statistics are equal to each other
    if sleep_stat2 == sleep_stat1:

        # if they are equal and the first is not Light sleep percentage, set the second as Light sleep percentage
        if sleep_stat1 != 'Light sleep percentage':
            sleep_stat2 = 'Light sleep percentage'

        # if they are equal and the first is Light sleep percentage, set the second as Deep sleep percentage
        else:
            sleep_stat2 = 'Deep sleep percentage'

    # filter out appropriate values
    cols = ['ID', sleep_stat1, sleep_stat2, SLEEP_EFFICIENCY_COL]
    filt_efficiency = filt_vals(df_sleep, slider_values, SLEEP_EFFICIENCY_COL, cols)

    # plot the sleep statistics in a density contour plot
    fig = px.density_contour(filt_efficiency, x=sleep_stat1, y=sleep_stat2, z='Sleep efficiency', histfunc="avg",
                             template='plotly_dark')
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)

    return fig


@app.callback(
    Output('smoke-vs-sleep', 'figure'),
    Input('efficiency-slider', 'value')
)
# ONLY SHOWING SLEEP EFFICIENCY BECAUSE THE DATA FOR THE OTHER COLUMNS DOES NOT MAKE SENSE
def show_sleep_strip(smoker_slider):
    """ Shows a strip chart that shows the relationship between a sleep variable and smoking status
    Args:
        smoker_slider (list of ints): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the strip chart itself
    """
    SMOKING_STATUS_COL = 'Smoking status'
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    # filter the data based on the sleep efficiency range
    cols = ['ID', SMOKING_STATUS_COL, SLEEP_EFFICIENCY_COL]
    sleep_smoking = filt_vals(EFFICIENCY, smoker_slider, SLEEP_EFFICIENCY_COL, cols)

    # plot the strip chart showing the relationship between smoking statuses and sleep efficiency
    fig = px.strip(sleep_smoking, x=SLEEP_EFFICIENCY_COL, y=SMOKING_STATUS_COL, color=SMOKING_STATUS_COL,
                   color_discrete_map={'Yes': 'forestgreen', 'No': 'red'}, template='plotly_dark')

    return fig


def _forest_reg(focus_col):
    """ Builds the random forest regressor model that predicts a y-variable
    Args:
        focus_col (str): name of the y-variable of interest
    Returns:
        random_forest_reg: fitted random forest regressor based on the dataset
    """
    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # extract data from dataframe
    x = df_sleep.loc[:, x_feat_list].values
    y = df_sleep.loc[:, focus_col].values

    # initialize a random forest regressor
    random_forest_reg = RandomForestRegressor()

    random_forest_reg.fit(x, y)

    return random_forest_reg


def _convert(gender, smoke):
    """ Encode the passed in variables to match encoding in the random forest regressor
    Args:
        gender (str): whether the user is Biological Male or Biological Female
        smoke (str): whether the user smokes or not
    Returns:
        gender_value (int): encoded variable representing gender of the user
        smoke_value (int): encoded variable representing whether the user smokes
    """
    if gender == 'Biological Male':
        gender_value = 1
    else:
        gender_value = 0

    if smoke == 'Yes':
        smoke_value = 1
    else:
        smoke_value = 0

    return gender_value, smoke_value


@app.callback(
    Output('sleep-eff', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-duration', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_eff_reg(age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their sleep efficiency given input of all these variables
    Args:
        age (int): the age of the user
        bedtime (float): user bedtime based on hours into the day (military time)
        wakeuptime (float): user wakeup time based on hours into the day (military time)
        duration (float): number of hours that the user was asleep (wakeup time minus bedtime)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine consumption in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol consumption in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted sleep efficiency
    """
    random_forest_reg = _forest_reg('Sleep efficiency')

    gender_value, smoke_value = _convert(gender, smoke)

    # user inputs turned into a numpy array
    data = np.array([[age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise,
                      gender_value, smoke_value]])

    # predict based on user inputs from the dropdown and sliders
    y_pred = random_forest_reg.predict(data)

    return 'Your predicted sleep efficiency (expressed in %) is \n{}'.format(round(float(y_pred), 2))


@app.callback(
    Output('sleep-rem', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-duration', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_rem_reg(age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their REM sleep percentage given input of all these variables
    Args:
        age (int): the age of the user
        bedtime (float): user bedtime based on hours into the day (military time)
        wakeuptime (float): user wakeup time based on hours into the day (military time)
        duration (float): number of hours that the user was asleep (wakeup time minus bedtime)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine consumption in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol consumption in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted REM sleep percentage
    """
    random_forest_reg = _forest_reg('REM sleep percentage')

    gender_value, smoke_value = _convert(gender, smoke)

    # user inputs turned into a numpy array
    data = np.array([[age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise,
                      gender_value, smoke_value]])

    # predict based on user inputs from the dropdown and sliders
    y_pred = random_forest_reg.predict(data)

    return 'Your predicted REM sleep percentage is \n{}'.format(round(float(y_pred), 2))


@app.callback(
    Output('sleep-deep', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-duration', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_deep_reg(age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their deep sleep percentage given input of all these variables
    Args:
        age (int): the age of the user
        bedtime (float): user bedtime based on hours into the day (military time)
        wakeuptime (float): user wakeup time based on hours into the day (military time)
        duration (float): number of hours that the user was asleep (wakeup time minus bedtime)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine consumption in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol consumption in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted deep sleep percentage
    """
    random_forest_reg = _forest_reg('Deep sleep percentage')

    gender_value, smoke_value = _convert(gender, smoke)

    # user inputs turned into a numpy array
    data = np.array([[age, bedtime, wakeuptime, duration, awakenings, caffeine, alcohol, exercise,
                      gender_value, smoke_value]])

    # predict based on user inputs from the dropdown and sliders
    y_pred = random_forest_reg.predict(data)

    return 'Your predicted deep sleep percentage is \n{}'.format(round(float(y_pred), 2))


def plot_feat_import_rf_reg(feat_list, feat_import, sort=True, limit=None):
    """ plots feature importances in a horizontal bar chart

    The x-axis is labeled accordingly for a random forest regressor

    Args:
        feat_list (list): str names of features
        feat_import (np.array): feature importances (mean MSE reduce)
        sort (bool): if True, sorts features in decreasing importance
            from top to bottom of plot
        limit (int): if passed, limits the number of features shown
            to this value
    Returns:
        None, just plots the feature importance bar chart
    """
    if sort:
        # sort features in decreasing importance
        idx = np.argsort(feat_import).astype(int)
        feat_list = [feat_list[_idx] for _idx in idx]
        feat_import = feat_import[idx]

    if limit is not None:
        # limit to the first limit feature
        feat_list = feat_list[:limit]
        feat_import = feat_import[:limit]

    fig = px.bar(x=feat_list, y=feat_import, labels={'x': 'Features', 'y': 'feature importance'},
                 template='plotly_dark')

    return fig


@app.callback(
    Output('feature-importance', 'figure'),
    Input('feature', 'value')
)
def plot_eff_forest(focus_col):
    """ Plot the feature importance graph for the y-variable that the user chooses
    Args:
        focus_col (str): interested y-variable (either sleep efficiency, rem sleep percentage, or deep sleep percentage
    Return:
        None (just a bar chart)
    """
    # Establish the theme of any visualizations
    sns.set()

    # Establish the features not used by the random forest regressor
    unwanted_feats = ['ID', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage']

    # we can represent binary categorical variables in single indicator tags via one-hot encoding
    df_sleep = pd.get_dummies(data=EFFICIENCY, columns=['Gender', 'Smoking status'], drop_first=True)

    # the x features for the regressor should be quantitative
    x_feat_list = list(df_sleep.columns)
    for feat in unwanted_feats:
        x_feat_list.remove(feat)

    # extract data from dataframe
    x = df_sleep.loc[:, x_feat_list].values
    y = df_sleep.loc[:, focus_col].values

    # creates a dictionary that maps features to their importance value
    # THIS SHOULD MAKE BE SHOWED TO THE USER ALONG WITH THE PLOT
    # sleep_important = make_feature_import_dict(featchosen, random_forest_reg.feature_importances_)
    # print(sleep_important)

    # initialize a random forest regressor
    random_forest_reg = RandomForestRegressor()

    random_forest_reg.fit(x, y)

    # plots the importance of features in determining a person's sleep efficiency by the random forest regressor
    fig = plot_feat_import_rf_reg(x_feat_list, random_forest_reg.feature_importances_)

    return fig


@app.callback(
    Output('three-dim-plot', 'figure'),
    Input('independent-3D-feat1', 'value'),
    Input('independent-3D-feat2', 'value'),
    Input('dependent-feature', 'value')
)
def plot_m_reg(x_var1, x_var2, focus_col):
    """
    x_var1 (str): one x-variable of interest
    x_var2 (str): another x-variable of interest
    focus_col (str): y-variable of interest
    """
    df_sleep = EFFICIENCY

    if x_var1 == 'Smoking status' or x_var1 == 'Smoking status':
        df_sleep = pd.get_dummies(data=df_sleep, columns=['Smoking status'], drop_first=True)
        df_sleep = df_sleep.rename(columns={'Smoking status_Yes': 'Smoking status'})

    # Create the linear regression model
    model = LinearRegression()

    # Fit the model
    model.fit(df_sleep[[x_var1, x_var2]], df_sleep[focus_col])

    # multiple linear regression plot
    fig = px.scatter_3d(df_sleep, x=x_var1, y=x_var2, z=focus_col, color='Gender', template='plotly_dark', width=710,
                        height=350)

    return fig


@app.callback(
    Output('sleep-hygiene', 'figure'),
    Input('radar-features', 'value')
)
def plot_sleep_hygiene(radar_features):
    """
    Makes a radar graph of sleep hygiene
    Args:
        radar_features (list of strings): a list of the features that will be represented on the radar graph
    Returns:
        None, just plots the radar graph
    """
    df_sleep = EFFICIENCY
    CAFFEINE_COL = 'Caffeine consumption'

    hygiene = df_sleep[radar_features]
    if CAFFEINE_COL in radar_features:
        hygiene[CAFFEINE_COL] = np.log(df_sleep[CAFFEINE_COL] + 1)

    fig = go.Figure()
    values = hygiene.values.tolist()

    for i in range(len(values)):
        fig.add_trace(go.Scatterpolar(
            r=values[i],
            theta=list(hygiene.columns),
            fill='toself',
            name='Person ' + str(i)
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )),
        showlegend=False,
        template='plotly_dark'
    )

    return fig


app.run_server(debug=True)
