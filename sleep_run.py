import sleep
from dash import Dash, Input, Output

app = Dash(__name__)


@app.callback(
    Output('ds-rem', 'figure'),
    Input('ds-slide', 'value')
)
def main(deepsleep):
    sleep.update_sleep_corr(deepsleep)


app.run_server(debug=True)


# call functions to make the sankey diagrams
if __name__ == '__main__':
    main()