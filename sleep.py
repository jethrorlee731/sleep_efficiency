"""
Colbe Chang, Jocelyn Ju, Jethro R. Lee, Michelle Wang, and Ceara Zhang
DS3500
Final Project: Sleep Efficiency Dashboard (sleep.py)
April 19, 2023

sleep.py: runs the general code for the dashboard
"""
# import statements
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import seaborn as sns
import numpy as np
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import utils

# read in the file as a dataframe and perform basic cleaning
EFFICIENCY = utils.read_file('data/Sleep_Efficiency.csv')

# parse the bedtime and wakeup times and convert them to military times
EFFICIENCY = utils.parse_times(EFFICIENCY)

app = Dash(__name__)

# layout for the dashboard
app.layout = html.Div([
    dcc.Tabs([
        # create a tab with the sleep statistic graphs
        dcc.Tab(label='Sleep Statistics', children=[
            html.Div([
                html.Div([
                    # add a header containing the title of the dashboard
                    html.H1("snoozeless", style={'textAlign': 'center', 'font-family': 'Cursive'}),

                    # Make a note that the viewer of the dashboard may have to adjust their zoom settings to see the
                    # dashboard properly
                    html.H2("NOTE: To see the dashboard properly formatted, you may have to adjust your window zoom "
                            "settings."),

                    # Define what "sleep efficiency" actually means
                    html.P('"Sleep efficiency" refers to the ratio of time that one rests in bed while actually '
                           'asleep.'),

                    # Explain the importance of sleep efficiency, REM sleep percentage, and deep sleep percentage
                    html.P('Allowing people to sleep the most efficiently is essential as the amount of rest we get '
                           'impacts our health and well-being every day. As college students, sleep is even more '
                           'precious and limited. We are all very interested in learning how to make the most of our '
                           'limited sleep times. Aside from us, people that fall into other demographic groups would '
                           'benefit from understanding what factors help to maximize REM sleep percentages or deep '
                           'sleep percentages. Sleep is a necessity, so it would be difficult for one to not be '
                           'interested in learning more about how to better their sleep through methods such as '
                           'maximizing the time they are in the deep sleep stage.'),
                    html.P("REM sleep is responsible for helping people process new knowledge and execute motor "
                           "skills to their fullest potential. Deep sleep enables the body to release vital growth "
                           "hormones that work to build muscles, tissues, and bones.")
                ], style={'background-color': 'blue', 'color': 'white'}
                ),

                dbc.Row([
                    # div for a dropdown that controls the dependent variable of the plots in the midnight blue region
                    html.Div([
                        html.P('Choose the dependent variable.',
                               style={'textAlign': 'center'}),

                        # drop down menu to choose the value represented on the y-axes of the plots in the midnight blue
                        # region
                        dcc.Dropdown(
                            ['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                             'Light sleep percentage', 'Awakenings', 'Caffeine consumption 24 hrs before sleeping (mg)',
                             'Alcohol consumption 24 hrs before sleeping (oz)', 'Exercise frequency (in days per week)',
                             'Age', 'Wakeup time', 'Bedtime'],
                            value='Sleep duration', id='sleep-stat-dep', style={'background-color': 'royalblue',
                                                                                'color': 'black'})
                    ], style={'background-color': 'midnightblue', 'color': 'white'}
                    )
                ]),

                dbc.Row([
                    # div containing the scatter plot and gender distribution plots
                    html.Div([
                        # div for a scatter plot comparing the relationship between two sleep variables
                        html.Div([
                            html.H2('How Certain Factors Affect Your Sleep Quality', style={'textAlign': 'center'}),
                            dcc.Graph(id='sleep-scatter',
                                      style={'display': 'inline-block', 'width': '45vw', 'height': '45vh'}),

                            # drop down menu that allows users to control the scatter plot's independent variable
                            html.P('Select an independent variable you are interested in observing.'),
                            dcc.Dropdown(
                                ['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage', 'Awakenings', 'Caffeine consumption 24 hrs before sleeping '
                                                                         '(mg)',
                                 'Alcohol consumption 24 hrs before sleeping (oz)', 'Exercise frequency (in '
                                                                                    'days per week)', 'Age',
                                 'Wakeup time', 'Bedtime'],
                                value='Age', clearable=False, id='sleep-stat-ind', style={'display': 'inline-block',
                                                                                          'width': '100%',
                                                                                          'background-color':
                                                                                              'royalblue',
                                                                                          'color': 'black'}),

                            # Add instructors that tell users how to control how much data gets represented
                            html.P('Adjust the axes values by brushing over points you want to inspect more closely',
                                   style={'textAlign': 'left'}),

                            # checkbox to toggle the trend-line on the scatter plot
                            dcc.Checklist(
                                ['Show Trend Line'],
                                ['Show Trend Line'], id='scatter-trend-line', inline=True,
                                style={'background-color': 'midnightblue'}
                            ),
                        ],
                            # Add style parameters to this Div
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

                            # div for a histogram distribution of a sleep statistic by gender
                            html.Div([
                                dcc.Graph(id='hist-gender', style={'display': 'inline-block', 'width': '49%'})
                            ]),

                            # checkbox that allows users to filter the violin plot and histogram by gender
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
                            html.P('Independent variables on the graph will default to different values if the same '
                                   'value is chosen for both independent variables in the dropdown menus'),
                            dcc.Graph(id='efficiency-contour', style={'display': 'inline-block', 'height': '45vh'}),

                            # drop down menu to choose the first independent variable for the density contour plot
                            html.P(
                                'Choose one independent variable to be represented in the density contour plot',
                                style={'textAlign': 'center'}),
                            dcc.Dropdown(
                                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage',
                                 'Awakenings', 'Caffeine consumption 24 hrs before sleeping (mg)', 'Alcohol '
                                                                                                   'consumption 24 hrs before sleeping (oz)',
                                 'Exercise frequency (in days per week)',
                                 'Age', 'Wakeup time', 'Bedtime', 'Gender', 'Smoking status'],
                                value='Awakenings', id='density-stat1',
                                style={'background-color': 'mediumslateblue',
                                       'color': 'black'}),

                            # drop down menu to choose the second independent variable for the density contour plot
                            html.P(
                                'Choose another variable to be represented in the density contour plot',
                                style={'textAlign': 'center'}),
                            dcc.Dropdown(
                                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage',
                                 'Light sleep percentage',
                                 'Awakenings', 'Caffeine consumption 24 hrs before sleeping (mg)', 'Alcohol '
                                                                                                   'consumption 24 hrs before sleeping (oz)',
                                 'Exercise frequency (in days per week)',
                                 'Age', 'Wakeup time', 'Bedtime', 'Gender', 'Smoking status'],
                                value='Light sleep percentage', id='density-stat2',
                                style={'background-color': 'mediumslateblue', 'color': 'black'})
                        ],
                            # Add style parameters to this Div
                            style={'width': '50%', 'display': 'inline-block', 'float': 'right',
                                   'background-color': 'indigo', 'height': '48vw'})]),

                    # div for the feature importance graph, sleep hygiene radial chart, and 3D scatter plot
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

                                # display the feature importance chart
                                dcc.Graph(id="feature-importance",
                                          style={'display': 'inline-block', 'width': '100%', 'height': '60%'})
                            ],
                                # Add style parameters to this Div
                                style={'width': '25%', 'display': 'inline-block', 'float': 'left',
                                       'background-color': 'darkviolet', 'height': '58vw'}),

                            # div for radar graph of sleep hygiene
                            html.Div([
                                html.H2('Sleep Hygiene', style={'textAlign': 'center'}),
                                dbc.Col([
                                    html.Div([
                                        # Ask user how many times they wake up in their sleep
                                        html.Div([
                                            html.P('How many times do you wake up during your sleep?',
                                                   style={'textAlign': 'center'}),
                                            dcc.Slider(0, 10, 1, value=1, marks=None, id='hygiene-awakening',
                                                       tooltip={"placement": "bottom", "always_visible": True})]),

                                        # Ask user how much caffeine they consume
                                        html.Div([
                                            html.P('How much caffeine do you consume 24 hrs prior to bedtime (in mg)?',
                                                   style={'textAlign': 'center'}),
                                            dcc.Slider(0, 1000, 50, value=1, marks=None, id='hygiene-caffeine',
                                                       tooltip={'placement': 'bottom', 'always_visible': True})]),
                                        # Ask user how much alcohol they consume
                                        html.Div([
                                            html.P('How much alcohol do you consume 24 hrs prior to bedtime (in oz)?',
                                                   style={'textAlign': 'center'}),
                                            dcc.Slider(0, 15, 1, value=1, marks=None, id='hygiene-alcohol',
                                                       tooltip={'placement': 'bottom', 'always_visible': True})
                                        ]),
                                        # Ask user how many times they exercise per week
                                        html.Div([
                                            html.P('How many times do you exercise per week?',
                                                   style={'textAlign': 'center'}),
                                            dcc.Slider(0, 10, 1, value=1, marks=None, id='hygiene-exercise',
                                                       tooltip={'placement': 'bottom', 'always_visible': True})
                                        ])

                                    ])]),
                                # plots the radar graph on the dashboard
                                dcc.Graph(id="sleep-hygiene", style={'display': 'inline-block', 'width': '100%'})

                            ],
                                # Add style parameters to this Div
                                style={'width': '30%', 'display': 'inline-block', 'float': 'left',
                                       'background-color': 'darkviolet', 'height': '58vw'}
                            ),

                            # div for a 3D scatter plot showing relationship between 2 independent sleep variables
                            # and 1 dependent sleep variable
                            html.Div([
                                html.H2('3D view of two independent variables against a chosen dependent variable',
                                        style={'textAlign': 'center'}),

                                # allows the users to control the two independent variables on the scatter plot
                                html.P('Select two independent variables you are interested in looking at.'),
                                dcc.Dropdown(
                                    ['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption 24 hrs before '
                                                                            'sleeping (mg)',
                                     'Alcohol consumption 24 hrs before sleeping (oz)', 'Exercise '
                                                                                        'frequency (in days per week)',
                                     'Age', 'Wakeup time', 'Bedtime', 'Smoking status'],
                                    value='Age', clearable=False, id='independent-3D-feat1',
                                    style={'background-color': 'mediumpurple', 'color': 'black'}),
                                dcc.Dropdown(
                                    ['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption 24 hrs before '
                                                                            'sleeping (mg)',
                                     'Alcohol consumption 24 hrs before sleeping (oz)', 'Exercise '
                                                                                        'frequency (in days per week)',
                                     'Age', 'Wakeup time', 'Bedtime', 'Smoking status'],
                                    value='Awakenings', clearable=False, id='independent-3D-feat2',
                                    style={'background-color': 'mediumpurple', 'color': 'black'}),

                                # allows users to control the dependent variable of the scatter plot
                                html.P('Select dependent variable you are interested in looking at.'),
                                dcc.Dropdown(['Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage'],
                                             value='Sleep efficiency',
                                             clearable=False, id='dependent-feature',
                                             style={'background-color': 'mediumpurple', 'color': 'black'}),

                                # instructs users as to how they can filter the scatter plot by gender
                                html.P(
                                    'Filter by gender in the 3D scatter by clicking in the legend on the gender '
                                    'that you do not want to focus on.'),
                                dcc.Graph(id="three-dim-plot", style={'display': 'inline-block', 'width': '50vw',
                                                                      'height': '50vw'})
                            ],
                                # Add style parameters to this Div
                                style={'width': '45%', 'display': 'inline-block', 'float': 'right',
                                       'background-color': 'darkviolet', 'height': '58vw'}
                            ),
                        ])
                    ])
                ]),
            ], style={'background-color': 'midnightblue', 'color': 'white'})
        ], style={'background-color': 'black', 'color': 'white'}),

        # tab containing a section in which users can find their predicted sleep efficiencies, REM sleep percentages,
        # and deep sleep percentages with a random forest regressor
        dcc.Tab(label='Sleep Quality Predictor', children=[
            html.Div([
                # div for calculating sleep efficiency, REM sleep percentage, and deep sleep percentage
                # based on the random forest regressor
                html.Div([
                    html.H2('Find your sleep efficiency, REM sleep percentage, and deep sleep percentage!',
                            style={'textAlign': 'center'}),

                    # guide users to a website that helps them determine how much REM and deep sleep they should get
                    html.Label([html.A('(What constitutes healthy REM and deep sleep percentages?)',
                                       style={'background-color': 'white'},
                                       href='https://www.healthline.com/health/how-much-deep-sleep-do-you-need#takeaway')], ),

                    # Ask user for information that are going to be inputs for the random forest regressor

                    # Div for sliders
                    dbc.Col([
                        html.Div([
                            # Ask a user for their age
                            html.Div([
                                html.P('How old are you?', style={'textAlign': 'center'}),
                                dcc.Slider(0, 100, 1, value=15, marks=None, id='sleep-age',
                                           tooltip={"placement": "bottom", "always_visible": True})]),

                            # Ask a user for their typical bedtime (as hours into the day)
                            html.Div([
                                html.P('What is your bedtime based on hours into the day (military time)?',
                                       style={'textAlign': 'center'}),
                                dcc.Slider(0, 24, 0.25, value=23, marks=None, id='sleep-bedtime',
                                           tooltip={'placement': 'bottom', 'always_visible': True})]),

                            # Ask a user for their typical wakeup time (hours into the day)
                            html.Div([
                                html.P('What is your wakeup time based on hours into the day (military time)?',
                                       style={'textAlign': 'center'}),
                                dcc.Slider(0, 24, 0.25, value=9, marks=None, id='sleep-wakeuptime',
                                           tooltip={'placement': 'bottom', 'always_visible': True})]),

                            # Ask a user for how much caffeine they consume in the 24 hours prior to bedtime (in mg)
                            html.Div([
                                html.P(
                                    'How much caffeine do you consume in the 24 hours prior to bedtime (in mg)?',
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

                            # Ask a user for the number of awakenings they have for a given night
                            html.Div([
                                html.P('What is the number of awakenings you have for a given night?',
                                       style={'textAlign': 'center'}),
                                dcc.Dropdown([0, 1, 2, 3, 4], value=0, clearable=False, id='sleep-awakenings',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user about their alcohol consumption in the 24 hours prior to bedtime (in oz)
                            html.Div([
                                html.P(
                                    'How much alcohol do you consume in the 24 hours prior to bedtime (in oz)?',
                                    style={'textAlign': 'center'}),
                                dcc.Dropdown([0, 1, 2, 3, 4, 5], value=0, clearable=False,
                                             id='sleep-alcohol',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user about whether they smoke/vape
                            html.Div([
                                html.P('Do you smoke/vape?', style={'textAlign': 'center'}),
                                dcc.Dropdown(['Yes', 'No'], value='No', clearable=False, id='sleep-smoke',
                                             style={'margin': 'auto', 'width': '70%', 'color': 'black'})]),

                            # Ask a user for the number of times they exercise per week
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
    # initialize the trend-line as None
    trend_line = None

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trend_line:
        trend_line = 'ols'

    # plot the relationship between the user-specified independent sleep statistic and user-specified dependent sleep
    # statistic (y) in a scatter plot
    fig = px.scatter(EFFICIENCY, x=sleep_stat_ind, y=sleep_stat_dep, trendline=trend_line, template='plotly_dark',
                     labels={'x': sleep_stat_ind, 'index': sleep_stat_dep})

    return fig


@app.callback(
    Output('violin-gender', 'figure'),
    Input('gender-options', 'value'),
    Input('sleep-stat-dep', 'value')
)
def show_sleep_gender_violin_plot(genders, sleep_stat):
    """ Shows a violin plot that represent distributions of a sleep statistic per gender
    Args:
        genders (list of str): list of genders to be shown on the violin plot
        sleep_stat (str): The statistic to be portrayed on the violin plot
    Returns:
        fig: the violin plot
    """
    # saving column names into constants
    GENDER_COL = 'Gender'

    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY[EFFICIENCY.Gender.isin(genders)]

    # plot the violin chart
    fig = px.violin(sleep_gender, x=GENDER_COL, y=sleep_stat, color=GENDER_COL, template='plotly_dark',
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
    # saving column names into constants
    GENDER_COL = 'Gender'

    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY[EFFICIENCY.Gender.isin(genders)]

    # plot the histogram
    # show multiple histograms color coded by biological gender if both the "male" and "female" checkboxes are ticked
    fig = px.histogram(sleep_gender, x=sleep_stat, color=GENDER_COL, template='plotly_dark',
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
        slider_values (list of floats): a range of average sleep efficiencies to be represented on the plot
    Returns:
        fig: the density contour plot
    """
    # saving sleep efficiency column into a constant
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    # performing one hot encoding if gender or smoking status needs to be shown on the plot
    df_sleep = utils.encode(sleep_stat1, sleep_stat2, EFFICIENCY)

    # change the second independent variable if it's the same with the first
    if sleep_stat1 == sleep_stat2:
        if sleep_stat1 != 'Awakenings':
            sleep_stat2 = 'Awakenings'
        else:
            sleep_stat2 = 'Caffeine consumption 24 hrs before sleeping (mg)'

    # filter out appropriate values
    cols = ['ID', sleep_stat1, sleep_stat2, SLEEP_EFFICIENCY_COL]
    filt_efficiency = utils.filt_vals(df_sleep, slider_values, SLEEP_EFFICIENCY_COL, cols)

    # plot the sleep statistics in a density contour plot
    fig = px.density_contour(filt_efficiency, x=sleep_stat1, y=sleep_stat2, z=SLEEP_EFFICIENCY_COL, histfunc="avg",
                             template='plotly_dark')
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)

    # update the x and y axis labels
    fig.update_layout(xaxis_title=sleep_stat1, yaxis_title=sleep_stat2)

    print(filt_efficiency)
    return fig


@app.callback(
    Output('smoke-vs-sleep', 'figure'),
    Input('efficiency-slider', 'value')
)
def show_sleep_strip(smoker_slider):
    """ Shows a strip chart that shows the relationship between a sleep variable and smoking status
    Args:
        smoker_slider (list of ints): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the strip chart itself
    """
    # saving column names into constants
    SMOKING_COL = 'Smoking status'
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    # filter the data based on the sleep efficiency range
    cols = ['ID', SMOKING_COL, SLEEP_EFFICIENCY_COL]
    sleep_smoking = utils.filt_vals(EFFICIENCY, smoker_slider, SLEEP_EFFICIENCY_COL, cols)

    # plot the strip chart showing the relationship between smoking statuses and sleep efficiency
    fig = px.strip(sleep_smoking, x=SLEEP_EFFICIENCY_COL, y=SMOKING_COL, color=SMOKING_COL,
                   color_discrete_map={'Yes': 'forestgreen', 'No': 'red'}, template='plotly_dark')

    return fig


@app.callback(
    Output('sleep-eff', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_eff_reg(age, bedtime, wakeuptime, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their predicted sleep efficiency given information about them
    Args:
        age (int): the age of the user
        bedtime (float): user's bedtime based on hours into the day (military time)
        wakeuptime (float): user's wakeup time based on hours into the day (military time)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine a user consumes in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol a user consumes in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted sleep efficiency
    """
    # predict sleep efficiency based on user inputs from the dropdown and sliders
    y_pred = utils.predict_sleep_quality('Sleep efficiency', EFFICIENCY, age, bedtime, wakeuptime, awakenings, caffeine,
                                         alcohol, exercise, gender, smoke)

    # display the user's predicted sleep efficiency
    return 'Your predicted sleep efficiency (expressed in %) is \n{}'.format(round(float(y_pred), 2))


@app.callback(
    Output('sleep-rem', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_rem_reg(age, bedtime, wakeuptime, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their predicted REM sleep percentage given information about them
    Args:
        age (int): the age of the user
        bedtime (float): user's bedtime based on hours into the day (military time)
        wakeuptime (float): user's wakeup time based on hours into the day (military time)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine a user consumes in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol a user consumes in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted REM sleep percentage
    """
    # predict REM sleep percentage based on user inputs from the dropdown and sliders
    y_pred = utils.predict_sleep_quality('REM sleep percentage', EFFICIENCY, age, bedtime, wakeuptime, awakenings,
                                         caffeine, alcohol, exercise, gender, smoke)

    # display the user's predicted sleep REM sleep percentage
    return 'Your predicted REM sleep percentage is \n{}'.format(round(float(y_pred), 2))


@app.callback(
    Output('sleep-deep', 'children'),
    Input('sleep-age', 'value'),
    Input('sleep-bedtime', 'value'),
    Input('sleep-wakeuptime', 'value'),
    Input('sleep-awakenings', 'value'),
    Input('sleep-caffeine', 'value'),
    Input('sleep-alcohol', 'value'),
    Input('sleep-exercise', 'value'),
    Input('sleep-gender', 'value'),
    Input('sleep-smoke', 'value')
)
def calc_deep_reg(age, bedtime, wakeuptime, awakenings, caffeine, alcohol, exercise, gender, smoke):
    """ Allow users to get their predicted deep sleep percentage given information about them
    Args:
        age (int): the age of the user
        bedtime (float): user's bedtime based on hours into the day (military time)
        wakeuptime (float): user's wakeup time based on hours into the day (military time)
        awakenings (int): number of awakenings a user has on a given night
        caffeine (int): amount of caffeine a user consumes in the 24 hours prior to bedtime (in mg)
        alcohol (int): amount of alcohol a user consumes in the 24 hours prior to bedtime (in oz)
        exercise (int): how many times the user exercises in a week
        gender (str): biological gender of the user
        smoke (str): whether the user smokes
    Returns:
        y_pred (float): predicted deep sleep percentage
    """
    # predict deep sleep percentage based on user inputs from the dropdown and sliders
    y_pred = utils.predict_sleep_quality('Deep sleep percentage', EFFICIENCY, age, bedtime, wakeuptime, awakenings,
                                         caffeine, alcohol, exercise, gender, smoke)

    # display the user's predicted sleep deep sleep percentage
    return 'Your predicted deep sleep percentage is \n{}'.format(round(float(y_pred), 2))


@app.callback(
    Output('feature-importance', 'figure'),
    Input('feature', 'value')
)
def plot_eff_forest(focus_col):
    """ Plot the feature importance graph for the y-variable that the user chooses
    Args:
        focus_col (str): y-variable of interest (sleep efficiency, REM sleep percentage, or deep sleep percentage)
    Return:
        fig: a bar chart containing the feature importance values
    """
    # Establish the theme of the visualization
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

    # Builds the random forest regressor model that predicts the user-specified y-variable for people
    random_forest_reg = utils.forest_reg(focus_col, EFFICIENCY)

    # plots the importance of features in determining the user-specified y variable for a person by the random forest
    # regressor
    fig = utils.plot_feat_import_rf_reg(x_feat_list, random_forest_reg.feature_importances_)

    return fig


@app.callback(
    Output('three-dim-plot', 'figure'),
    Input('independent-3D-feat1', 'value'),
    Input('independent-3D-feat2', 'value'),
    Input('dependent-feature', 'value')
)
def plot_three_dim_scatter(sleep_stat_x, sleep_stat_y, sleep_stat_z):
    """ Plot a 3d scatter plot showing the relationship between 3 sleep variables
    Args:
        sleep_stat_x (str): one sleep variable of interest
        sleep_stat_y (str): another sleep variable of interest
        sleep_stat_z (str): another sleep variable of interest
    Returns:
        fig: a 3d scatter plot
    """
    # performing one hot encoding if gender or smoking status needs to be shown on the plot
    df_sleep = utils.encode(sleep_stat_x, sleep_stat_y, EFFICIENCY)

    # plot the 3d scatter plot
    fig = px.scatter_3d(df_sleep, x=sleep_stat_x, y=sleep_stat_y, z=sleep_stat_z, color='Gender',
                        template='plotly_dark', width=633, height=455)

    return fig


@app.callback(
    Output('sleep-hygiene', 'figure'),
    Input('hygiene-awakening', 'value'),
    Input('hygiene-caffeine', 'value'),
    Input('hygiene-alcohol', 'value'),
    Input('hygiene-exercise', 'value')
)
def plot_sleep_hygiene(awakenings, caffeine, alcohol, exercise):
    """ Makes a radar graph of sleep hygiene
    Args:
        awakenings (int) - how many times the user wakes up during sleep
        caffeine (int) - the amount of caffeine the user takes in 24 hrs prior to bedtime (in mg)
        alcohol (int) - the amount of alcohol the user drinks in 24 hrs prior to bedtime (in oz)
        exercise (int) - the number of times the user exercises per week
    Returns:
        fig: the radar graph itself
    """
    # saving the sleep efficiency data frame into a variable
    df_sleep = EFFICIENCY.copy()

    # saving column names as constants
    CAFFEINE_COL = 'Caffeine consumption 24 hrs before sleeping (mg)'

    # Getting the necessary columns for measuring hygiene
    hygiene = df_sleep[['Awakenings', 'Caffeine consumption 24 hrs before sleeping (mg)', 'Alcohol consumption 24 hrs '
                                                                                          'before sleeping (oz)',
                        'Exercise frequency (in days per week)']]
    hygiene[CAFFEINE_COL] = np.log(hygiene[CAFFEINE_COL] + 1)

    # getting average values of all columns
    average_hygiene = hygiene.mean()
    avg_values = average_hygiene.values.tolist()

    # creating the figure
    fig = go.Figure()
    # adding a plot to the graph - graph of the average person's hygiene
    fig.add_trace(go.Scatterpolar(
        r=avg_values,
        theta=list(hygiene.columns),
        fill='toself',
        name='Average Person'
    ))

    # Getting the user's input values
    caffeine = np.log(caffeine + 1)
    user_values = [awakenings, caffeine, alcohol, exercise]

    # adding a plot to the graph - graph of the user's hygiene
    fig.add_trace(go.Scatterpolar(
        r=user_values,
        theta=list(hygiene.columns),
        fill='toself',
        name='Your hygiene'
    ))

    # update the layout of the radar graph
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        template='plotly_dark',
        width=427,
        height=347
    )

    return fig


def main():
    # run app
    app.run_server(debug=True)


main()
