import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

file = 'data/Sleep_Efficiency.csv'

df = pd.read_csv(file).dropna()
hygiene = df[['Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency']]
hygiene['Caffeine consumption'] = np.log(df['Caffeine consumption'] + 1)
df_transposed = hygiene.T

data = []

fig = go.Figure()
values = hygiene.values.tolist()



for i in range(len(values)):
    fig.add_trace(go.Scatterpolar(
        r = values[i],
        theta = list(hygiene.columns),
        fill = 'toself',
        name = 'Person ' + str(i)
    ))




fig.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 5]
    )),
  showlegend=False
)

fig.show()




