table_suffix = '_test07a'
topic = 'ecg_000000'
topic += table_suffix

import os
import sys
import time
import psycopg2
from psycopg2 import errors
import plotly.express as px
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from helper_dash import *
import random

plot_margin = 0.03
fs_max = 500
window_width_s = 4
refresh_ms = 500

# postgres connection parameters
db_ip = os.environ['psqlIp']
db_port = os.environ['psqlPort']
db_su = os.environ['db_super_user']
db_su_pwd = os.environ['db_su_pwd']
db_name = os.environ['dbName']
conn = psycopg2.connect(user=db_su, password=db_su_pwd
                        , host=db_ip, port=db_port
                        , database=db_name)

# metadata_dict = {'number_of_segments': int(metadata_tuple[0])
#                     , 'patient_id': metadata_tuple[1]
#                     , 'patient_age': float(metadata_tuple[2])
#                     , 'target_HR': float(metadata_tuple[3])
#                     , 'measurement_datetime': metadata_tuple[4]
#                     , 'fs_Hz': float(metadata_tuple[5])}


metadata = getMetadata(conn, topic, table_suffix)
fs_orz = metadata['fs_Hz']
df_batch_length = int(np.ceil(refresh_ms * metadata['target_HR'] / 20000))
max_df_length = int(np.ceil(window_width_s * metadata['target_HR'] / 20))
if fs_max < fs_orz:
    interp_factor = int(np.ceil(fs_orz/fs_max))
else:
    interp_factor = 1
fs = fs_orz/interp_factor
num_points = int(window_width_s*fs+1)
# externalStylesheets = [ "https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.min.css"
#                        , "https://fonts.googleapis.com/css?family=Raleway:400,400i,700,700i"
#                        , "https://codepen.io/chriddyp/pen/bWLwgP.css"
#                        , "https://fonts.googleapis.com/css?family=Product+Sans:400,400i,700,700i"
#                        ]
# styles = {
#     'pre': {
#         'border': 'thin lightgrey solid',
#         'overflowX': 'scroll'
#     }
# }
# app = dash.Dash(__name__, external_stylesheets=externalStylesheets)


################################################################################

################################################################################

app = dash.Dash(__name__)
# server = app.server
app.layout = html.Div(children=[
    html.Div(html.H2('ECG live-view: '+topic))
    , html.Div(html.H3('x: Time (s)'))
    , html.Div(html.H3('y: ECG Signal (uV)'))
    , html.Div([
        dcc.Graph(id='live-graph', animate=False)
        , dcc.Input(id='topic', value=topic, type='text')
        , dcc.Interval(id='graph-update', interval=refresh_ms)
    ])
])

idx0 = -1
data_df = pd.DataFrame()
time_plt0 = 0.
time_s = []
signal = []
x_range_padding = window_width_s * plot_margin
print(interp_factor,num_points)

@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals'
                  # , component_id='topic', component_property='value'
                     )])
def update_graph_scatter(topic):
    global data_df
    global idx0
    global time_plt0
    global time_s
    global signal
    
    if not time_s or time_s[-1] < time_plt0 + window_width_s:
        data_df, idx0 = getData(data_df, idx0, df_batch_length)
        time_s, signal = get_data_go(data_df)
      
    idx_plt0 = time_s.index(time_plt0)
    
    idx_plt1 = idx_plt0 + num_points
    X = time_s[idx_plt0:idx_plt1]
    Y = signal[idx_plt0:idx_plt1]
    
    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )
    
    y_range_padding = (max(Y) - min(Y)) * plot_margin
    x_axis_min = min(X) - x_range_padding
    x_axis_max = max(X) + x_range_padding
    y_axis_min = min(Y) - y_range_padding
    y_axis_max = max(Y) + y_range_padding
    
    time_plt0 += refresh_ms/1000
    orig_stdout = sys.stdout
    f = open('out.txt', 'a')
    sys.stdout = f
    print('Intervals Passed: ' + str(time_plt0))
    sys.stdout = orig_stdout
    f.close()
    
    return {'data': [data], 'layout': go.Layout(xaxis={'range': [x_axis_min, x_axis_max]}
                                                , yaxis={'range': [y_axis_min, y_axis_max]}
                                                )}


################################################################################
def getData(data_df, idx0, df_batch_length):
    sql_get_latest_data = ("""
            SELECT
                DISTINCT (segment_index) as idx
              , P_s
              , Q_s
              , R_s
              , S_s
              , T_s
              , fs_Hz
              , patient_id
              , measurement_datetime
              , segment_start_time_s
              , signal
            FROM
                %s
            WHERE
                segment_index >= %s
            ORDER BY
                idx
            LIMIT
                %s
                """) % (topic, idx0, df_batch_length)

    while True:
        df = pd.read_sql(sql_get_latest_data, conn)
        if len(df) > 0:
            ids = list(df['idx'])
            for i in range(df_batch_length):
                idx = idx0 + 1 + i
                if idx in ids:
                    data_df = data_df.append(df.iloc[i], ignore_index=True)
                    idx1 = idx
            break
        else:
            time.sleep(0.05)
   
    data_df = data_df.iloc[-max_df_length:]
    return data_df, idx1


def get_data_go(data_df):
    time_0 = data_df['segment_start_time_s'].iloc[0]
    signal = data_df['signal'].explode().apply(float).to_list()
    time_s = [time_0 + i / fs_orz for i in range(len(signal))]
    
    idx_0 = int((time_0 * 1000) % (1000 / fs_max))
    time_s = time_s[idx_0::interp_factor]
    signal = signal[idx_0::interp_factor]

    return time_s, signal


if __name__ == '__main__':
    app_host = os.environ['app_host']
    app_port = int(os.environ['app_port'])
    app.run_server(debug=True
        , host=app_host, port=app_port,
                   )