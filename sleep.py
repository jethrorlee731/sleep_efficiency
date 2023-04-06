from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import numpy as np

# read the csv files into dataframes
efficiency = pd.read_csv('data/Sleep_Efficiency.csv')
# I JUST DID THIS FOR NOW SO WE DON'T RUN INTO ISSUES WITH NA VALUES BELOW. WE CAN FIX THIS BY REPLACING WITH MEDIAN
# OF THE COLUMN IF WE WANT.
EFFICIENCY = efficiency.copy()
EFFICIENCY = EFFICIENCY.dropna()
TIMES = pd.read_csv('data/sleepdata_2.csv')

app = Dash(__name__)

# multiply sleep efficiencies by 100 to represent them as percentages
EFFICIENCY.loc[:, 'Sleep efficiency'] = EFFICIENCY['Sleep efficiency'] * 100
# EFFICIENCY.loc[:, 'Sleep efficiency'] = EFFICIENCY['Sleep efficiency'].apply(lambda x: x*100)

# WE SHOULD GIVE AN INTRODUCTION AT THE TOP OF THE DASHBOARD REGARDING HOW WE THINK LOOKING AT SLEEP EFFICIENCY
# , REM SLEEP PERCENTAGE, AND DEEP SLEEP PERCENTAGE ARE ALL VERY IMPORTANT. REM SLEEP IS RESPONSIBLE FOR HELPING
# THE BRAIN PROCESS NEW LEARNINGS AND MOTOR SKILLS FOR THE DAY. DEEP SLEEP IS RESPONSIBLE FOR ALLOWING THE
# BODY TO RELEASE GROWTH HORMONES AND WORKS TO BUILD AND REPAIR MUSCLES, BONES, AND TISSUES

# layout for the dashboard
# WE CAN DECIDE ON THE FORMAT OF THE LAYOUT LATER AND USE CHILDRENS TO REFORMAT

app.layout = html.Div([
    html.H1("snoozless", style={'textAlign': 'center'}),

    # Define what "sleep efficiency" actually means
    html.P('"Sleep efficiency" refers to the ratio of time that one rests in bed while actually asleep'),

    # div for drop down filter for all the plots except the machine learning models, strip chart, and deep contour plot
    html.Div([
        html.P('Choose the dependent variable (sleep duration by default, including when invalid values are chosen)',
               style={'textAlign': 'center'}),

        # drop down menu to choose the value represented on the y-axis
        dcc.Dropdown(['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                      'Light sleep percentage', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                      'Exercise frequency'], value='Sleep duration', id='sleep-stat-dep')
    ]),

    # div containing the scatter plot and gender distribution plots
    # div for a scatter plot comparing the relationship between two sleep variables
    html.Div([
        html.Div([
            html.H2('How Certain Factors Affect Your Sleep Quality', style={'textAlign': 'center'}),
            dcc.Graph(id='sleep-scatter', style={'display': 'inline-block', 'width': '45vw', 'height': '45vh'}),

            html.P('Select an independent variable you are interested in observing.'),
            dcc.Dropdown(['Sleep duration', 'Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage',
                          'Light sleep percentage', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                          'Exercise frequency'],
                         value='Age', clearable=False, id='sleep-stat-ind',
                         style={'display': 'inline-block'}),

            # A slider that allows the user to control how much of the dependent variable gets represented
            html.P('Adjust the Percentage Range of the Dependent Variable', style={'textAlign': 'left'}),
            dcc.RangeSlider(0, 100, 1, value=[0, 100], id='sleep-scatter-slider', marks=None,
                            tooltip={"placement": "bottom", "always_visible": True}),

            # checkbox to toggle trend-line
            dcc.Checklist(
                ['Show Trend Line'],
                ['Show Trend Line'], id='scatter-trend-line', inline=True
            ),
        ],
            # Add style parameters to this Div, placing it in the left 49% of the page
            style={'width': '49%', 'display': 'inline-block', 'float': 'left', 'height': '45vh'}),

        # div for comparing sleep statistic distributions between genders
        html.Div([
            html.H2('Sleep Statistics Across Genders', style={'textAlign': 'center'}),
            # div for violin plot distributions of a sleep statistic by gender
            html.Div([
                dcc.Graph(id='violin-gender', style={'display': 'inline-block', 'width': '49%', 'float': 'left'})
            ]),

            # div for histogram distribution of a sleep statistic by gender (uses the same checkbox as the violin plot)
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
            # Add style parameters to this Div, placing it in the right 49% of the page
            style={'width': '49%', 'display': 'inline-block'}),
    ]),

    # div for strip and density plots
    html.Div([
        # div for smoking status strip chart
        html.Div([
            # creating a strip chart showing the relationship between one's smoking status and a sleep variable
            html.H2('How Smoking Affects Your Sleep Quality', style={'textAlign': 'center'}),
            dcc.Graph(id='smoke-vs-sleep', style={'display': 'inline-block'}),

            # sleep efficiency slider
            html.P('Adjust Sleep Efficiency Percentage', style={'textAlign': 'left'}),
            dcc.RangeSlider(50, 100, 1, value=[50, 100], id='smoker-slider',
                            tooltip={"placement": "bottom", "always_visible": True}, marks=None),

            # specify to the users how they can filter the data by smoking status
            html.P("Click in the legend on smoking statuses you don't want represented on the plot"),
        ],
            # Add style parameters to this Div, placing it in the left 49% of the page
            style={'width': '49%', 'display': 'inline-block', 'float': 'left'}),

        # div for density contour plot (comparing a combination of variables with sleep efficiency)
        html.Div([
            html.H2('How Various Features Affect Sleep Efficiency', style={'textAlign': 'center'}),
            dcc.Graph(id='efficiency-contour', style={'display': 'inline-block', 'height': '45vh'}),

            html.P(
                'Choose one independent variable to be represented in the density contour plot (sleep duration by '
                'default, including when invalid values are chosen)',
                style={'textAlign': 'center'}),

            # drop down menu to choose the first independent variable for the density contour plot
            dcc.Dropdown(
                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage',
                 'Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency'],
                value='Sleep duration', id='density-stat1'),

            html.P(
                'Choose the another variable to be represented in the density contour plot (light sleep percentage by '
                'default, including when invalid values are chosen)',
                style={'textAlign': 'center'}),

            # drop down menu to choose the second independent variable for the density contour plot
            dcc.Dropdown(
                ['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage',
                 'Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency'],
                value='Light sleep percentage', id='density-stat2'),

            # sleep efficiency slider
            html.P('Adjust the Represented Sleep Efficiency Values', style={'textAlign': 'left'}),
            dcc.RangeSlider(50, 100, 1, value=[50, 100], marks=None,
                            tooltip={"placement": "bottom", "always_visible": True},
                            id='efficiency-slide')
        ],
            # Add style parameters to this Div, placing it in the right 49% of the page
            style={'width': '49%', 'display': 'inline-block', 'float': 'right'}),
    ]),

    # div for machine learning components
    html.Div([
        # div for calculating sleep efficiency, REM sleep percentage, and Deep sleep percentage
        # based on the multiple learning regression model
        html.Div([
            html.H2('Find your sleep efficiency, REM sleep percentage, and deep sleep percentage!',
                    style={'textAlign': 'center'}),

            # Ask user information that are going to be inputs into the multiple learning regression model

            # Ask a user for their age
            html.P('How old are you?', style={'textAlign': 'center'}),
            dcc.Slider(0, 100, 1, value=15, marks=None, id='sleep-age',
                       tooltip={"placement": "bottom", "always_visible": True}),

            # Ask a user for they gender they identify with
            html.P("What's your biological gender?", style={'textAlign': 'center'}),
            dcc.Dropdown(['Biological Male', 'Biological Female'], value='Biological Male',
                         clearable=False, id='sleep-gender'),

            # Ask a user what is their bedtime (hours into the day)
            html.P('What is your bedtime based on hours into the day (military time)?',
                   style={'textAlign': 'center'}),
            dcc.Slider(0, 24, 0.25, value=23, marks=None, id='sleep-bedtime', tooltip={'placement': 'bottom',
                                                                                       'always_visible': True}),

            # Ask a user what is their wakeup time (hours into the day)
            html.P('What is your wakeup time based on hours into the day (military time)?',
                   style={'textAlign': 'center'}),
            dcc.Slider(0, 24, 0.25, value=9, marks=None, id='sleep-wakeuptime', tooltip={'placement': 'bottom',
                                                                                         'always_visible': True}),

            # Ask a user how long they sleep for (wakeup time minus bedtime)
            html.P('What is the total amount of time you slept (in hours)?', style={'textAlign': 'center'}),
            dcc.Slider(0, 15, 0.25, value=7, marks=None, id='sleep-duration', tooltip={'placement': 'bottom',
                                                                                       'always_visible': True}),

            # Ask a user the number of awakenings they have for a given night
            html.P('What is the number of awakenings you have for a given night?', style={'textAlign': 'center'}),
            dcc.Dropdown([0, 1, 2, 3, 4], value=0, clearable=False, id='sleep-awakenings'),

            # Ask a user the amount of caffeine consumption in the 24 hours prior to bedtime (in mg)
            html.P('What is your amount of caffeine consumption in the 24 hours prior to bedtime (in mg)?',
                   style={'textAlign': 'center'}), dcc.Slider(0, 200, 1, value=50,
                                                              marks=None, id='sleep-caffeine',
                                                              tooltip={'placement': 'bottom',
                                                                       'always_visible': True}),

            # Ask a user the amount of alcohol consumption in the 24 hours prior to bedtime (in oz)
            html.P('What is your amount of alcohol consumption in the 24 hours prior to bedtime (in oz)?',
                   style={'textAlign': 'center'}), dcc.Dropdown([0, 1, 2, 3, 4, 5], value=0, clearable=False,
                                                                id='sleep-alcohol'),

            # Ask a user about whether they smoke/vape
            html.P('Do you smoke/vape?', style={'textAlign': 'center'}),
            dcc.Dropdown(['Yes', 'No'], value='No', clearable=False, id='sleep-smoke'),

            # Ask a user the number of times the test subject exercises per week
            html.P('How many times do you exercise per week?', style={'textAlign': 'center'}),
            dcc.Dropdown([0, 1, 2, 3, 4, 5], value=2, clearable=False, id='sleep-exercise'),

            html.Br(),
            html.H2(id='sleep-eff', style={'textAlign': 'center'}),
            html.H2(id='sleep-rem', style={'textAlign': 'center'}),
            html.H2(id='sleep-deep', style={'textAlign': 'center'})
        ],
            # Add style parameters to this Div, placing it in the left 33% of the dashboard and making it shorter
            style={'width': '30%', 'display': 'inline-block', 'float': 'left', 'height': '10vh'}),

        # div for the two graphs created by a random forest regressor and multiple regression model
        html.Div([
            html.Div([
                html.H2('Which variables are most important in determining sleep efficiency, '
                        'REM sleep percentage, or deep sleep percentage?',
                        style={'textAlign': 'center'}),
                html.P('Select which dependent variable you are interested in looking at.'),
                dcc.Dropdown(['Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage'],
                             value='Sleep efficiency',
                             clearable=False, id='feature', style={'margin': 'auto', 'width': '60%'}),
                dcc.Graph(id="feature-importance", style={'display': 'inline-block', 'width': '100%', 'height': '45vh'})
            ],
                # Add style parameters to this Div, placing it in the left 49% of the right column
                style={'width': '49%', 'display': 'inline-block', 'float': 'left'}),

            html.Div([
                html.H2('3D view of two independent variables against a chosen dependent variable',
                        style={'textAlign': 'center'}),
                html.P('Select three independent variables you are interested in looking at.'),
                dcc.Dropdown(['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                              'Exercise frequency'],
                             value='Age', clearable=False, id='independent-3D-feat1'),
                dcc.Dropdown(['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption', 'Alcohol consumption',
                              'Exercise frequency'],
                             value='Awakenings', clearable=False, id='independent-3D-feat2'),
                html.P('Select dependent variable you are interested in looking at.'),
                dcc.Dropdown(['Sleep efficiency', 'REM sleep percentage', 'Deep sleep percentage'],
                             value='Sleep efficiency',
                             clearable=False, id='dependent-feature'),
                html.P('Filter by gender in the 3D scatter by clicking in the legend on the gender that you are not '
                       'interested in.'),
                dcc.Graph(id="three-dim-plot", style={'display': 'inline-block', 'width': '100%'})
            ],
                # Add style parameters to this Div, placing it in the right 49% of the right column
                style={'width': '49%', 'display': 'inline-block', 'float': 'right'}
            )
        ],
            # Add style parameters to this Div, placing it in the right 70% of the page
            style={'width': '70%', 'display': 'inline-block', 'float': 'right'}
        )
    ])
])


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


def _parse_times(df_sleep, sleep_stat):
    """ Parses the bedtime and wakeup time columns in the sleep data frame to contain decimals that represent times
    Args:
        df_sleep (Pandas data frame): a data frame containing sleep statistics for test subjects
        sleep_stat (str): The statistic to be portrayed on the box plot
    Returns:
        sleep_df (Pandas data frame): a newer version of the data frame with the parsed times
    """
    # make a copy of the dataframe to act upon
    df_new = df_sleep

    # parse the bedtime columns to only include hours into the day
    if sleep_stat == 'Bedtime':
        df_new['Bedtime'] = df_new['Bedtime'].str.split().str[1]
        df_new['Bedtime'] = df_new['Bedtime'].str[:2].astype(float) + df_sleep['Bedtime'].str[3:5].astype(float) / 60


    # parse the wakeup time columns to only include hours into the day
    elif sleep_stat == 'Wakeup time':
        df_new['Wakeup time'] = df_new['Wakeup time'].str.split().str[1]
        df_new['Wakeup time'] = df_new['Wakeup time'].str[:2].astype(float) + \
                                df_new['Wakeup time'].str[3:5].astype(float) / 60
        # df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str.split().str[1]
        # df_sleep['Wakeup time'] = df_sleep['Wakeup time'].str[:2].astype(float) + \
        #                           df_sleep['Wakeup time'].str[3:5].astype(float) / 60

    # Parse no data if neither the bedtime or wakeup time columns are specified via the sleep_stat parameter
    # else:
    #     None

    return df_new


@app.callback(
    Output('sleep-scatter', 'figure'),
    Input('sleep-scatter-slider', 'value'),
    Input('scatter-trend-line', 'value'),
    Input('sleep-stat-ind', 'value'),
    Input('sleep-stat-dep', 'value')
)
def make_sleep_scatter(slider_values, show_trendline, sleep_stat_ind, sleep_stat_dep):
    """ Creates a scatter plot showing the relationship between two sleep statistics
    Args:
        slider_values (list of floats): a range of values for the independent variable to be represented on the plot
        show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
        sleep_stat_ind (string): the independent variable of the scatter plot
        sleep_stat_dep (string): the dependent variable of the scatter plot

    Returns:
        fig (px.scatter): the scatter plot itself
    """
    # set the default y statistic to "Sleep Duration"
    if sleep_stat_dep in [None, sleep_stat_ind]:
        sleep_stat_dep = 'Sleep duration'

    # initialize the trend-line as None
    trend_line = None

    # filter out appropriate values
    cols = ['ID', sleep_stat_ind, sleep_stat_dep]
    filt_deepsleep = filt_vals(EFFICIENCY, slider_values, sleep_stat_dep, cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_deepsleep = _parse_times(filt_deepsleep, sleep_stat_ind)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trend_line = 'ols'

    # plot the sleep statistic (x) and the other sleep statistic (y)
    fig = px.scatter(filt_deepsleep, x=sleep_stat_ind, y=sleep_stat_dep, trendline=trend_line,
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

    # column containing values for a subject's biological gender
    GENDER_COL = 'Gender'

    # set the default of the dependent variable of the violin plot to be sleep duration if the dependent variable
    # chosen is invalid or non-existent
    if sleep_stat in [None, 'Deep sleep percentage', 'Alcohol consumption', 'Caffeine consumption',
                      'Exercise frequency', 'Bedtime', 'Wakeup time']:
        sleep_stat = 'Sleep duration'

    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY.loc[EFFICIENCY.Gender.isin(genders),]

    # plot the violin chart
    fig = px.violin(sleep_gender, x='Gender', y=sleep_stat, color=GENDER_COL,
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
    # column containing values for a subject's biological gender
    GENDER_COL = 'Gender'

    # set the default of the dependent variable of the violin plot to be sleep duration if the dependent variable
    # chosen is invalid or non-existent
    if sleep_stat in [None, 'Deep sleep percentage', 'Alcohol consumption', 'Caffeine consumption',
                      'Exercise frequency', 'Bedtime', 'Wakeup time']:
        sleep_stat = 'Sleep duration'

    # filter the data based on the chosen genders
    sleep_gender = EFFICIENCY.loc[EFFICIENCY.Gender.isin(genders),]

    # plot the histogram
    # show multiple histograms color coded by biological gender if both the "male" and "female" checkboxes are ticked
    fig = px.histogram(sleep_gender, x=sleep_stat, color=GENDER_COL,
                       color_discrete_map={'Female': 'sienna', 'Male': 'blue'})

    return fig


@app.callback(
    Output('efficiency-contour', 'figure'),
    Input('density-stat1', 'value'),
    Input('density-stat2', 'value'),
    Input('efficiency-slide', 'value')
)
def show_efficiency_contour(sleep_stat1, sleep_stat2, slider_values):
    """ Shows a density contour plots that shows the relationship between two variables and average sleep efficiency
    Args:
        sleep_stat1 (str): One statistic to be portrayed on the density contour plot
        sleep_stat2 (str): Another statistic to be portrayed on the density contour plot
        slider_values (list of floats): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the density contour plot
    """
    # assign a variable name to the string "Sleep efficiency"
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    # check whether the sleep statistics are equal to each other
    if sleep_stat2 == sleep_stat1:

        # if they are equal and the first is not Light sleep percentage, set the second as Light sleep percentage
        if sleep_stat1 != 'Light sleep percentage':
            sleep_stat2 = 'Light sleep percentage'

        # otherside, set the second as Deep sleep percentage
        else:
            sleep_stat2 = 'Deep sleep percentage'

    # filter out appropriate values
    cols = ['ID', sleep_stat1, sleep_stat2, SLEEP_EFFICIENCY_COL]
    filt_efficiency = filt_vals(EFFICIENCY, slider_values, SLEEP_EFFICIENCY_COL, cols)

    # plot the sleep statistics in a density contour plot
    fig = px.density_contour(filt_efficiency, x=sleep_stat1, y=sleep_stat2, z='Sleep efficiency', histfunc="avg")
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)

    return fig


# parse the times for bedtime and wakeup time from the EFFICIENCY dataframe
filt_parsed = _parse_times(EFFICIENCY, "Bedtime")
filt_parsed = _parse_times(filt_parsed, "Wakeup time")


@app.callback(
    Output('smoke-vs-sleep', 'figure'),
    Input('smoker-slider', 'value')
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
                   color_discrete_map={'Yes': 'forestgreen', 'No': 'red'})

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
    df_sleep = pd.get_dummies(data=filt_parsed, columns=['Gender', 'Smoking status'], drop_first=True)

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

    fig = px.bar(x=feat_list, y=feat_import, labels={'x': 'Features', 'y': 'feature importance'})

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
    df_sleep = pd.get_dummies(data=filt_parsed, columns=['Gender', 'Smoking status'], drop_first=True)

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
    x_var3 (str): 3rd x-variable of interest
    focus_col (str): y-variable of interest
    """
    # Create the linear regression model
    model = LinearRegression()

    # Fit the model
    model.fit(filt_parsed[[x_var1, x_var2]], filt_parsed[focus_col])

    # mutliple linear regression plot
    fig = px.scatter_3d(filt_parsed, x=x_var1, y=x_var2, z=focus_col, color='Gender')

    return fig


app.run_server(debug=True)
