# import os
# import sys
# import psycopg2
# import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
from dash.dependencies import Input, Output
import random

plot_margin = 0.03
fs = 500
window_width = 6
refresh_ms = 500



externalStylesheets = [ "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css"
                       , "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i"
                       , "https://codepen.io/chriddyp/pen/bWLwgP.css"
                       , "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
                       ]
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
app = dash.Dash(__name__, external_stylesheets=externalStylesheets)
app.layout = html.Div([
    dcc.Graph(id='live-graph', animate=False),
    dcc.Interval(
        id='graph-update',
        interval=refresh_ms
    )
])

# X = deque(maxlen=window_width*fs)
# Y = deque(maxlen=window_width*fs)

num_points = window_width*fs
num_new_points = int(refresh_ms*fs/1000)
X = [0+0.001*x for x in range(num_points)]
Y = list(np.random.rand(num_points))

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    global X, Y
    X.extend([max(X) + 0.001 + 0.001 * x for x in range(num_new_points)])
    Y.extend(list(np.random.rand(num_new_points)))
    X = X[-num_points:]
    Y = Y[-num_points:]
    
    data = go.Scatter(
        x=X,
        y=Y,
        name='Scatter',
        mode='lines+markers'
    )
    
    x_range_padding = (max(X)-min(X))*plot_margin
    y_range_padding = (max(Y)-min(Y))*plot_margin
    
    return {'data': [data], 'layout': go.Layout( xaxis=dict(range=[ min(X)-x_range_padding
                                                                  , max(X)+x_range_padding])
                                               , yaxis=dict(range=[ min(Y)-y_range_padding
                                                                  , max(Y)+y_range_padding])
                                               )}


if __name__ == '__main__':
    app.run_server(debug=True
                   , port=8080
                   , host='ec2-54-189-36-235.us-west-2.compute.amazonaws.com')
