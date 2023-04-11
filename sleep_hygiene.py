import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go

file = 'data/Sleep_Efficiency.csv'

df = pd.read_csv(file).dropna()
hygiene = df[['Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency']]
hygiene['Caffeine consumption'] = np.log(df['Caffeine consumption'] + 1)
average_hygiene = hygiene.mean()




fig = go.Figure()
values = average_hygiene.values.tolist()




fig.add_trace(go.Scatterpolar(
    r = values,
    theta = list(hygiene.columns),
    fill = 'toself',
    name = 'Average Person'
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




