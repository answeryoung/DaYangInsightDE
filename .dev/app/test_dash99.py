table_suffix = '_test07a'
topic = 'ecg_002093'
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
from helper_dash import getMetadata
import random
from matplotlib import pyplot as plt

plot_margin = 0.01
fs_max = 500
window_width_s = 6
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
df_batch_length = int(np.ceil(refresh_ms * metadata['target_HR'] / 30000))
max_df_length = int(np.ceil(window_width_s * metadata['target_HR'] / 20))
number_of_segments = metadata['number_of_segments']
if fs_max < fs_orz:
    interp_factor = int(np.ceil(fs_orz / fs_max))
else:
    interp_factor = 1
fs = fs_orz / interp_factor
num_points = int(window_width_s * fs + 1)
num_points_orz = int(window_width_s * fs_orz + interp_factor)
num_shift_points = int(refresh_ms / 1000 * fs)
num_shift_points_orz = int(refresh_ms / 1000 * fs_orz)
time_step = round(1 / fs, 3)
time_step_orz = round(1 / fs_orz, 3)

################################################################################

################################################################################

app = dash.Dash(__name__)
# server = app.server
app.layout = html.Div(children=[
    html.Div(html.H4('ECG live-view: ' + topic))
    , html.Div(html.H5('Patient Id: ' + metadata['patient_id']))
    , html.Div(html.H5('Measurement S/N: ' + metadata['measurement_datetime']))
    , html.Div(html.H5('Patient Age: ' + str(int(metadata['patient_age']))))
    , html.Div([
        dcc.Graph(id='live-graph', animate=False)
        , dcc.Interval(id='graph-update', interval=refresh_ms*0.9)
    ])
])

# init persistent variables
idx0 = -1
time_plt0 = -window_width_s
time_s = np.arange(-window_width_s, 0, time_step)
signal = np.zeros(num_points-1)
t_features = []
v_features = []
x_range_padding = window_width_s * plot_margin


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(unused_var):
    global idx0
    global time_plt0
    global time_s
    global signal
    global t_features
    
    if time_s[-1] < time_s[0] + window_width_s + 2 and idx0 < number_of_segments-1:
        idx0, time_s, signal, t_features = \
            getData(idx0, df_batch_length, time_s, signal, t_features)
    
    data, time_s, signal, t_features, axes_lim = \
        getDataGo(num_points, num_shift_points, time_s, signal, t_features)
    
    return {'data': data, 'layout': go.Layout(
        xaxis={'title': 'Time (s)', 'range': axes_lim['X']}
        , yaxis={'title': 'ECG Signal (uV)', 'range': axes_lim['Y']}
    )}


################################################################################
def getData(idx_lim, batch_length, time_input, signal_input, t_features_input):
    sql_get_latest_data = ("""
            SELECT
                DISTINCT (segment_index) as idx
              , P_s
              , Q_s
              , R_s
              , S_s
              , T_s
              , segment_start_time_s
              , signal
            FROM
                %s
            WHERE
                segment_index > %s
            ORDER BY
                segment_index
            LIMIT
                %s
                """) % (topic, idx_lim, batch_length)
    
    data_df = pd.DataFrame()
    while True:
        df = pd.read_sql(sql_get_latest_data, conn)
        if len(df) > 0:
            ids = list(df['idx'])
            for i in range(df_batch_length):
                idx = idx_lim + 1 + i
                if idx in ids:
                    data_df = data_df.append(df.iloc[i], ignore_index=True)
                    idx_fin = idx
                else:
                    break
            break
        else:
            time.sleep(0.05)

    time_0 = round(data_df['segment_start_time_s'].iloc[0], 3)
    idx_0 = round((time_0 * 1000) % (1000 / fs))
    signal_cur = data_df['signal'].explode().apply(float).to_numpy()
    time_cur = np.arange(time_0, time_0 + len(signal_cur) * time_step_orz, time_step_orz)
    signal_cur = signal_cur[idx_0::interp_factor]
    time_cur = time_cur[idx_0::interp_factor]
    time_output = np.concatenate((time_input, time_cur), axis=None)
    signal_output = np.concatenate((signal_input, signal_cur), axis=None)
    
    t_features_cur = data_df.loc[:, ['p_s', 'q_s', 'r_s', 's_s', 't_s']].to_numpy()
    if len(t_features_input) == 0:
        t_features_output = t_features_cur
    else:
        t_features_output = np.concatenate((t_features_input, t_features_cur), axis=0)
   
    return idx_fin, time_output, signal_output, t_features_output


def getDataGo(n_points, n_shift_points, time_s_input, signal_input, t_features_input):
    X = time_s_input[0:n_points]
    Y = signal_input[0:n_points]
    time_s_output = time_s_input[n_shift_points:]
    signal_output = signal_input[n_shift_points:]
    signal_go = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Signal',
        mode='lines+markers'
    )
    
    f0 = np.argwhere(t_features_input[:, 4] > X[0]).min()
    ff = np.argwhere(t_features_input[:, 1] > X[-1]).min()
    t_features_curr = t_features_input[f0:ff, :]
    for x, y in \
            np.concatenate((np.argwhere(t_features_curr < X[0]), np.argwhere(t_features_curr > X[-1])), axis=0):
        t_features_curr[x,y] = np.nan
    wf = interp1d(X, Y)
    v_features_curr = wf(t_features_curr)

    data = [signal_go]
    feature_names = ['P-peak','Q-peak','R-peak','S-peak','T-peak']
    for p in range(5):
        data.append(
            go.Scatter(
                x=list(t_features_curr[:, p])
                , y=list(v_features_curr[:, p])
                , name=feature_names[p]
                , mode='markers'
                , marker=dict(size=12)
            )
        )
    
    axes_lim = {}
    y_range_padding = (max(Y) - min(Y)) * 5 * plot_margin
    axes_lim['X'] = [min(X) - x_range_padding, max(X) + x_range_padding]
    axes_lim['Y'] = [-1000, 1500]
    # axes_lim['Y'] = [min(Y) - y_range_padding, max(Y) + y_range_padding]
    
    # data = [signal_go]
    # data.append(signal_go)
    t_features_output = t_features_input[f0:, :]
    # data = [signal_go, signal_go2]
    return data, time_s_output, signal_output, t_features_output, axes_lim


if __name__ == '__main__':
    app_host = os.environ['app_host']
    app_port = int(os.environ['app_port'])
    app.run_server(debug=True
                   , port=app_port, host=app_host
                   )
