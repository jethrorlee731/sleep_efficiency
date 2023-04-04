from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import sleep_reg as sr
import sleep_forest as sf

# read the csv files into dataframes
EFFICIENCY = pd.read_csv('data/Sleep_Efficiency.csv')
TIMES = pd.read_csv('data/sleepdata_2.csv')
app = Dash(__name__)

# WE CAN EITHER MULTIPLY THE VALUES UP HERE OR ALTER THE COLUMN AFTER TAKING DEEP COPIES OF EFFICIENCY IN THE SCATTER
# FUNCTIONS. WE CANNOT JUST ENTER THIS LINE IN OUR SCATTER PLOT FUNCTIONS FOR THE SLEEP EFFICIENCY VALUES WOULD MULTIPLY
# BY 100 INDEFINITELY AS THE PROGRAM KEEPS RUNNING. - Jethro

# multiply sleep efficiencies by 100 to represent them as percentages
EFFICIENCY['Sleep efficiency'] = EFFICIENCY['Sleep efficiency'] * 100

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
        dcc.RangeSlider(18, 30, 1, value=[18, 30], id='ds-slide-deep', marks=None,
                        tooltip={"placement": "bottom", "always_visible": True})]),

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
        dcc.RangeSlider(15, 30, 1, value=[15, 30], id='ds-slide-rem', marks=None,
                        tooltip={"placement": "bottom", "always_visible": True})]),

    # div for Sleep Efficiency vs. other variables
    html.Div([
        html.H2('Sleep Efficiency (expressed in %) vs. Sleep Statistics', style={'textAlign': 'center'}),
        dcc.Graph(id='ds-sleep', style={'display': 'inline-block'}),

        # checkbox to toggle trendline
        dcc.Checklist(
            ['Show Trend Line'],
            ['Show Trend Line'], id='scatter_trendline-sleep', inline=True
        ),

        # deep sleep slider
        html.P('Adjust Sleep Efficiency Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(50, 100, 1, value=[50, 100], id='ds-slide-sleep', marks=None,
                        tooltip={"placement": "bottom", "always_visible": True})]),

    # div for Box Plot Distributions by Gender
    html.Div([
        html.H2('Distribution by Gender', style={'textAlign': 'center'}),
        dcc.Graph(id='box-gender', style={'display': 'inline-block'}),

        # checkboxes that allow users to filter the data by gender
        dcc.Checklist(
            ['Male', 'Female'],
            ['Male', 'Female'], id='box-gender-options', inline=True
        )]),

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
        dcc.RangeSlider(0, 23, 0.5, value=[0, 23], id='bd-slide', marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}),

        # slider for wakeup time
        html.P('Adjust Wakeup Time', style={'textAlign': 'left'}),
        dcc.RangeSlider(3, 12.5, 0.5, value=[3, 12.5], id='wu-slide', marks=None,
                        tooltip={"placement": "bottom", "always_visible": True}),
    ]),

    # div for density contour plot (comparing a combination of variables with sleep efficiency)
    html.Div([
        html.H2('How Various Features Affect Sleep Efficiency', style={'textAlign': 'center'}),
        dcc.Graph(id='efficiency-contour', style={'display': 'inline-block'}),

        html.P('Choose one independent variable to be represented in the density contour plot (sleep duration by '
               'default, including when invalid values are chosen)',
               style={'textAlign': 'center'}),

        # drop down menu to choose the first independent variable for the density contour plot
        dcc.Dropdown(['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage',
                      'Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency'],
                     value='Sleep duration', id='density-stat1'),

        html.P('Choose the another variable to be represented in the density contour plot (light sleep percentage by '
               'default, including when invalid values are chosen)',
               style={'textAlign': 'center'}),

        # drop down menu to choose the second independent variable for the density contour plot
        dcc.Dropdown(['Sleep duration', 'REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage',
                      'Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency'],
                     value='Light sleep percentage', id='density-stat2'),

        # deep sleep slider
        html.P('Adjust the Represented Sleep Efficiency Values', style={'textAlign': 'left'}),
        dcc.RangeSlider(50, 100, 1, value=[50, 100], marks=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        id='efficiency-slide')]),

    # div for smoking status strip chart

    html.Div([
        # creating a strip chart showing the relationship between one's smoking status and a sleep variable
        html.H2('How Smoking Affects Your Sleep Quality', style={'textAlign': 'center'}),
        dcc.Graph(id='smoke-vs-sleep', style={'display': 'inline-block'}),

        # sleep efficiency slider
        html.P('Adjust Sleep Efficiency Percentage', style={'textAlign': 'left'}),
        dcc.RangeSlider(50, 100, 1, value=[50, 100], id='smoker-slider',
                        tooltip={"placement": "bottom", "always_visible": True}, marks=None),

        # checkbox that allows users to filter the data by smoking status
        html.P('Filter by smoking status'),
        dcc.Checklist(
            ['Smokers', 'Non-smokers'],
            ['Smokers', 'Non-smokers'], id='strip-smoker-options', inline=True)
    ]),

    # div for calculating sleep score
    html.Div([
        html.H2('Find your sleep score!', style={'textAlign': 'center'}),

        # Ask user for information that could affect their sleep efficiency

        # Ask a user for their age
        html.P('How old are you?', style={'textAlign': 'center'}),
        dcc.Slider(0, 100, 1, value=0, marks=None, id='sleep-score-age',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user for they gender they identify with
        html.P("What's your biological gender?", style={'textAlign': 'center'}),
        dcc.Dropdown(['Biological Male', 'Biological Female'], clearable=False, id='sleep-score-gender'),

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

        # Ask a user about their exercise habits per day
        html.P('How many minutes of moderate aerobic exercise do you typically get in a day?',
               style={'textAlign': 'center'}),
        dcc.Slider(0, 180, 1, value=0, marks=None, id='sleep-score-exercise',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user about whether they smoke/vape
        html.P('Do you smoke/vape?', style={'textAlign': 'center'}),
        dcc.Dropdown(['Yes', 'No'], clearable=False, id='sleep-score-smoke'),

        # Ask a user about how many hours of sleep they get, on average, per day
        html.P('On average, how many hours do you sleep in a day?', style={'textAlign': 'center'}),
        dcc.Slider(0, 24, 1, value=0, marks=None, id='sleep-score-duration',
                   tooltip={"placement": "bottom", "always_visible": True}),

        # Ask a user how many cups of caffeine they consume per week
        html.P('On average, how many cups of caffeine do you consume per week?', style={'textAlign': 'center'}),
        dcc.Slider(0, 10, 1, value=0, marks=None, id='sleep-score-caffeine',
                   tooltip={"placement": "bottom", "always_visible": True}),

        html.Br(),
        html.H2(id='sleep-score', style={'textAlign': 'center'})

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


def _parse_times(df_sleep, sleep_stat):
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
    # else:
    #     None

    return df_sleep


def _sleep_scatter(slider_values, show_trendline, sleep_stat_x, sleep_stat_y):
    """ Creates a scatter plot showing the relationship between two sleep statistics
    Args:
        slider_values (list of floats): a range of values for the independent variable to be represented on the plot
        show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
        sleep_stat_x (string): the independent variable of the scatter plot
        sleep_stat_y (string): the dependent variable of the scatter plot

    Returns:
        fig (px.scatter): the scatter plot itself
    """
    if sleep_stat_y in [None, sleep_stat_x]:
        sleep_stat_y = 'Sleep duration'

    trendline = None

    # filter out appropriate values
    cols = ['ID', sleep_stat_x, sleep_stat_y]
    filt_deepsleep = filt_vals(EFFICIENCY, slider_values, sleep_stat_x, cols)

    # change the times in the data frame to represent hours into a day as floats if they are getting plotted
    filt_deepsleep = _parse_times(filt_deepsleep, sleep_stat_y)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    fig = px.scatter(filt_deepsleep, x=sleep_stat_x, y=sleep_stat_y, trendline=trendline,
                     labels={'x': sleep_stat_x, 'index': sleep_stat_y})

    return fig


@app.callback(
    Output('ds-deep', 'figure'),
    Input('ds-slide-deep', 'value'),
    Input('scatter_trendline-deep', 'value'),
    Input('sleep-stat', 'value')
)
def update_deep_sleep(deepsleep, show_trendline, sleep_stat):
    """ Creates a scatter plot showing the relationship between deep sleep percentage and another sleep statistic
        Args:
            deepsleep (list of floats): a range of deep sleep percentages to be represented on the plot
            show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
            sleep_stat (string): the dependent variable of the scatter plot

        Returns:
            fig (px.scatter): the deep sleep percentage vs. sleep statistic scatter plot itself
    """
    fig = _sleep_scatter(deepsleep, show_trendline, 'Deep sleep percentage', sleep_stat)

    return fig


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide-rem', 'value'),
    Input('scatter_trendline-rem', 'value'),
    Input('sleep-stat', 'value')
)
def update_rem_sleep(remsleep, show_trendline, sleep_stat):
    """ Creates a scatter plot showing the relationship between REM sleep percentage and another sleep statistic
        Args:
            remsleep (list of floats): a range of REM sleep percentages to be represented on the plot
            show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
            sleep_stat (string): the dependent variable of the scatter plot

        Returns:
            fig (px.scatter): the REM sleep percentage vs. sleep statistic scatter plot itself
    """
    fig = _sleep_scatter(remsleep, show_trendline, 'REM sleep percentage', sleep_stat)

    return fig


@app.callback(
    Output('ds-sleep', 'figure'),
    Input('ds-slide-sleep', 'value'),
    Input('scatter_trendline-sleep', 'value'),
    Input('sleep-stat', 'value')
)
def update_sleep_eff(sleepeff, show_trendline, sleep_stat):
    """ Creates a scatter plot showing the relationship between sleep efficiency and another sleep statistic
        Args:
            sleepeff (list of floats): a range of sleep efficiencies to be represented on the plot
            show_trendline (string): a string indicating whether a trend line should appear on the scatter plot
            sleep_stat (string): the dependent variable of the scatter plot

        Returns:
            fig (px.scatter): the sleep efficiency percentage vs. sleep statistic scatter plot itself
    """
    fig = _sleep_scatter(sleepeff, show_trendline, 'Sleep efficiency', sleep_stat)

    return fig


@app.callback(
    Output('box-gender', 'figure'),
    Input('box-gender-options', 'value'),
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
    sleep_gender = EFFICIENCY.loc[EFFICIENCY.Gender.isin(genders), ]

    # plot the box and whisker chart
    fig = px.box(sleep_gender, x='Gender', y=sleep_stat, color='Gender',
                 color_discrete_map={'Female': 'sienna', 'Male': 'blue'}, labels={sleep_stat: ylabel})

    return fig


@app.callback(
    Output('efficiency-contour', 'figure'),
    Input('density-stat1', 'value'),
    Input('density-stat2', 'value'),
    Input('efficiency-slide', 'value')
)
def show_efficiency_contour(sleep_stat1, sleep_stat2, slider_values):
    """
    Shows a density contour plots that shows the relationship between two variables and average sleep efficiency
    Args:
        sleep_stat1 (str): One statistic to be portrayed on the box plot
        sleep_stat2 (str): Another statistic to be portrayed on the box plot
        slider_values (list of floats): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the density contour plot
    """
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    if sleep_stat2 == sleep_stat1:
        if sleep_stat1 != 'Light sleep percentage':
            sleep_stat2 = 'Light sleep percentage'
        else:
            sleep_stat2 = 'Deep sleep percentage'

    # filter out appropriate values
    cols = ['ID', sleep_stat1, sleep_stat2, SLEEP_EFFICIENCY_COL]
    filt_efficiency = filt_vals(EFFICIENCY, slider_values, SLEEP_EFFICIENCY_COL, cols)

    fig = px.density_contour(filt_efficiency, x=sleep_stat1, y=sleep_stat2, z='Sleep efficiency', histfunc="avg")
    fig.update_traces(contours_coloring="fill", contours_showlabels=True)

    return fig


@app.callback(
    Output('smoke-vs-sleep', 'figure'),
    Input('strip-smoker-options', 'value'),
    Input('smoker-slider', 'value')
)
# ONLY SHOWING SLEEP EFFICIENCY BECAUSE THE DATA FOR THE OTHER COLUMNS DOES NOT MAKE SENSE
def show_sleep_strip(user_responses, smoker_slider):
    """
    Shows a strip chart that shows the relationship between a sleep variable and smoking status
    Args:
        user_responses (list of str): List of smoking statuses that the user wants to be portrayed in the strip chart
        smoker_slider (list of ints): a range of sleep efficiencies to be represented on the plot
    Returns:
        fig: the strip chart itself
    """
    smoking_statuses = []
    SMOKING_STATUS_COL = 'Smoking status'
    SLEEP_EFFICIENCY_COL = 'Sleep efficiency'

    for user_response in user_responses:
        if user_response == 'Smokers':
            smoking_statuses.append('Yes')
        elif user_response == 'Non-smokers':
            smoking_statuses.append('No')

    # filter the data based on the chosen smoking statuses and sleep efficiency range
    cols = ['ID', SMOKING_STATUS_COL, SLEEP_EFFICIENCY_COL]
    sleep_smoking = EFFICIENCY.loc[EFFICIENCY[SMOKING_STATUS_COL].isin(smoking_statuses), ]
    sleep_smoking = filt_vals(sleep_smoking, smoker_slider, SLEEP_EFFICIENCY_COL, cols)

    fig = px.strip(sleep_smoking, x=SLEEP_EFFICIENCY_COL, y=SMOKING_STATUS_COL, color=SMOKING_STATUS_COL,
                   color_discrete_map={'Yes': 'forestgreen', 'No': 'red'})

    return fig


# parse the Bedtime and Wakeup time for the EFFICIENCY dataframe
_parse_times(EFFICIENCY, "Bedtime")
_parse_times(EFFICIENCY, 'Wakeup time')


@app.callback(
    Output('bd-wu', 'figure'),
    Input('bd-slide', 'value'),
    Input('wu-slide', 'value'),
    Input('scatter_trendline-bdwu', 'value')
)
def update_sleep_corr(bedtime, wakeup, show_trendline):
    """ Display the correlation between bedtime and wake time
        Args:
            bedtime (list): a list containing floats of the Bedtimes to display
            wakeup (list): a list containing floats of the Wakeup times to display
            show_trendline (string): a string indicating whether a trend line should appear on the scatter plot

        Returns:
            fig (px.scatter): the bedtime vs. the wakeup times
    """
    trendline = None

    # filter out appropriate values
    cols = ['ID', 'Bedtime', 'Wakeup time']

    filt_bedtime = filt_vals(EFFICIENCY, bedtime, 'Bedtime', cols)
    filt_both = filt_vals(filt_bedtime, wakeup, 'Wakeup time', cols)

    # show a trend line or not based on the user's input
    if 'Show Trend Line' in show_trendline:
        trendline = 'ols'

    # plot the data
    fig = px.scatter(filt_both, x='Bedtime', y='Wakeup time', trendline=trendline)

    return fig


@app.callback(
    Output('sleep-score', 'children'),
    Input('sleep-score-age', 'value'),
    Input('sleep-score-alcohol', 'value'),
    Input('sleep-score-exercise', 'value'),
    Input('sleep-score-smoke', 'value'),
    Input('sleep-score-duration', 'value'),
    Input('sleep-score-caffeine', 'value'),
    Input('sleep-score-gender', 'value')
)
def calculate_sleep_score(age, alcohol_intake, exercise_freq, is_smoker, sleep_duration, caffeine_intake, bio_gender):
    ALCOHOL_WEIGHT = 0.014327937359475853
    EXERCISE_WEIGHT = 0.009108186817433802
    SMOKING_WEIGHT = 0.02321723448127149
    DURATION_WEIGHT = 0.010390620689821457
    CAFFEINE_WEIGHT = 0.003953260547066465

    MAX_SCORE = 100

    alcohol_score = 0
    exercise_score = 0
    duration_score = 0

    # changes the sleep score based on one's alcohol intake
    if bio_gender == 'Biological Male':
        if alcohol_intake > 2:
            alcohol_score = 0
        elif alcohol_intake == 2:
            alcohol_score = 50
        elif 1 < alcohol_intake < 2:
            alcohol_score = 80
        else:
            alcohol_score = MAX_SCORE

    elif bio_gender == 'Biological Female':
        if alcohol_intake > 1:
            alcohol_score = 0
        elif alcohol_intake == 1:
            alcohol_score = 50
        elif alcohol_intake < 1:
            alcohol_score = MAX_SCORE

    # changes the sleep score based on one's exercise habits
    if exercise_freq >= 30:
        exercise_score = MAX_SCORE
    elif 20 <= exercise_freq < 30:
        exercise_score = 80
    elif 10 <= exercise_freq < 20:
        exercise_score = 50
    elif exercise_freq < 10:
        exercise_score = 0

    # changes the sleep score based on one's smoking habits
    if is_smoker == 'Yes':
        smoking_score = 50
    else:
        smoking_score = MAX_SCORE

    # changes the sleep score based on one's sleep duration habits
    if age == 0:
        if sleep_duration >= 14:
            duration_score = MAX_SCORE
        elif 10 <= sleep_duration < 14:
            duration_score = 50
        else:
            duration_score = 0
    elif 1 <= age <= 2:
        if sleep_duration >= 11:
            duration_score = MAX_SCORE
        elif 7 <= sleep_duration < 11:
            duration_score = 50
        else:
            duration_score = 0
    elif 3 <= age <= 5:
        if sleep_duration >= 10:
            duration_score = MAX_SCORE
        elif 6 <= sleep_duration < 10:
            duration_score = 50
        else:
            duration_score = 0
    elif 6 <= age <= 12:
        if sleep_duration >= 9:
            duration_score = MAX_SCORE
        elif 5 <= sleep_duration < 9:
            duration_score = 50
        else:
            duration_score = 0
    elif 13 <= age <= 18:
        if sleep_duration >= 8:
            duration_score = MAX_SCORE
        elif 4 <= sleep_duration < 8:
            duration_score = 50
        else:
            duration_score = 0
    elif age > 18:
        if sleep_duration >= 7:
            duration_score = MAX_SCORE
        elif 3 <= sleep_duration < 7:
            duration_score = 50
        else:
            duration_score = 0

    # changes the sleep score based on one's caffeine consumption habits
    if caffeine_intake >= 4:
        caffeine_score = 0
    elif 2 <= caffeine_intake < 4:
        caffeine_score = 50
    elif caffeine_intake == 1:
        caffeine_score = 80
    else:
        caffeine_score = MAX_SCORE

    sleep_score_raw = alcohol_score * ALCOHOL_WEIGHT + exercise_score * EXERCISE_WEIGHT + smoking_score * \
                      SMOKING_WEIGHT + duration_score * DURATION_WEIGHT + caffeine_score * CAFFEINE_WEIGHT
    sleep_score_max = MAX_SCORE * (ALCOHOL_WEIGHT + EXERCISE_WEIGHT + SMOKING_WEIGHT + DURATION_WEIGHT +
                                   CAFFEINE_WEIGHT)
    print(alcohol_score, exercise_score, smoking_score, duration_score, caffeine_score)
    sleep_score_actual = (sleep_score_raw / sleep_score_max) * 100
    return 'Your sleep score out of 100 is: \n{}'.format(sleep_score_actual)

def calc_eff_reg():

    pass

def calculate_eff_forest():
    pass


app.run_server(debug=True)
