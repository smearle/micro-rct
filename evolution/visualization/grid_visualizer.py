import plotly.graph_objects as go

import pandas as pd
import numpy as np
class GridVisualizer:
    def __init__(self, df):
        # take in raw map. We need to convert this to df
        self.df = df

    def visualize(self, x, y, val, write_path=None, x_skip=1, y_skip=1):
        temp = self.df.pivot(index=y, columns=x)[val]
        # temp = temp.fillna(-10)
        temp = temp.reindex(list(range(0, temp.index.max()+1, y_skip)), fill_value=np.nan)
        #temporary transpose to fill in missing column values
        temp = temp.T
        temp = temp.reindex(list(range(0, temp.index.max()+1, x_skip)), fill_value=np.nan)
        temp = temp.T
        fig = go.Figure(data=go.Heatmap(
            z=temp.values.tolist(),
            x=temp.columns.tolist(),
            y=temp.index.tolist(),
            # labels=dict(x="X", y="Y", Z="Fitness"),
            colorscale='Plasma'))
        fig['layout'].update(
            title=dict(
                text="Elite Map"
            ),
            xaxis=dict(
                showgrid=False,
                title=dict(text=temp.columns.name)),
            yaxis=dict(
                showgrid=False,
                title=dict(text=temp.index.name)),
        )
        fig['layout']['yaxis']['autorange'] = "reversed"

        
        if write_path != None:
            fig.write_html(write_path)
        
        
