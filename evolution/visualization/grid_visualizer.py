import plotly.express as px
import pandas as pd
import numpy as np
class GridVisualizer:
    def __init__(self, df):
        # take in raw map. We need to convert this to df
        self.df = df

    def visualize(self, x, y, val, write_path=None):
        temp = self.df.pivot(index=y, columns=x)[val]
        # temp = temp.fillna(-10)
        temp = temp.reindex(list(range(temp.index.min(), temp.index.max()+1)), fill_value=np.nan)
        #temporary transpose to fill in missing column values
        temp = temp.T
        temp = temp.reindex(list(range(temp.index.min(), temp.index.max()+1)), fill_value=np.nan)
        temp = temp.T
        fig = px.imshow(temp)
        fig['layout'].update(plot_bgcolor='rgb(203, 213, 232)')
        if write_path != None:
            fig.write_html(write_path)
        
        
