import sleep
from dash import Dash, Input, Output

app = Dash(__name__)


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide-deep', 'value'),
    Input('ds-slide-rem', 'value'),
    Input('ds-slide-sleep', 'value'),
    Input('bd-slide', 'value'),
    Input('wu-slide', 'value')
)
def main(deepsleep, remsleep, sleepeff, bedtime, wakeup):
    sleep.update_deep_sleep(deepsleep)
    sleep.update_rem_sleep(remsleep)
    sleep.update_sleep_eff(sleepeff)
    sleep.update_bd_corr(bedtime)
    sleep.update_wu_corr(wakeup)

    app.run_server(debug=True)


# call functions to make the sankey diagrams
if __name__ == '__main__':
    main()