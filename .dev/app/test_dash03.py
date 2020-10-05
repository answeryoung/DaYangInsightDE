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
from helper_dash import *
import random

plot_margin = 0.01
fs_max = 1000
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
df_batch_length = int(np.ceil(refresh_ms * metadata['target_HR'] / 60000))
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
        # , dcc.Input(id='topic', value=topic, type='text')
        , dcc.Interval(id='graph-update', interval=refresh_ms)
    ])
])
# init persistent variables
idx0 = -1
# data_df = pd.DataFrame()
time_plt0 = -window_width_s
time_s = np.arange(-window_width_s, 0, time_step)
signal = np.zeros(num_points)
x_range_padding = window_width_s * plot_margin


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(unused_var):
    # global data_df
    global idx0
    global time_plt0
    global time_s
    global signal
    
    if time_s[-1] < time_s[0] + window_width_s + 0.5 and idx0 < number_of_segments - 1:
        data_df, idx0 = getData(idx0, df_batch_length=df_batch_length)
        time_s, signal = get_data_go(data_df, time_s, signal)
    
    # idx_plt0 = time_s.index(time_plt0)
    # idx_plt1 = idx_plt0 + num_points
    # X = time_s[0:num_points_orz:2]
    # Y = signal[0:num_points_orz:2]
    X = time_s[0:num_points]
    Y = signal[0:num_points]
    
    data = go.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
        # mode='markers'
    )
    
    y_range_padding = (max(Y) - min(Y)) * plot_margin
    x_axis_min = min(X) - x_range_padding
    x_axis_max = max(X) + x_range_padding
    y_axis_min = min(Y) - y_range_padding
    y_axis_max = max(Y) + y_range_padding
    # y_axis_min = -750
    # y_axis_max = 1250
    
    # time_plt0 += refresh_ms/1000
    # time_s = time_s[num_shift_points_orz:]
    # signal = signal[num_shift_points_orz:]
    time_s = time_s[num_shift_points:]
    signal = signal[num_shift_points:]
    
    return {'data': [data], 'layout': go.Layout(
        xaxis={'title': 'Time (s)', 'range': [x_axis_min, x_axis_max]}
        , yaxis={'title': 'ECG Signal (uV)', 'range': [y_axis_min, y_axis_max]}
    )}


################################################################################
def getData(idx_lim, df_batch_length):
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
                segment_index > %s
            ORDER BY
                idx
            LIMIT
                %s
                """) % (topic, idx_lim, df_batch_length)
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
    return data_df, idx_fin


def get_data_go(df, time_input, signal_input):
    time_0 = round(df['segment_start_time_s'].iloc[0], 3)
    idx_0 = round((time_0 * 1000) % (1000 / fs))
    signal_cur = df['signal'].explode().apply(float).to_numpy()
    time_cur = np.arange(time_0, time_0 + len(signal_cur) * time_step_orz, time_step_orz)
    signal_cur = signal_cur[idx_0::interp_factor]
    time_cur = time_cur[idx_0::interp_factor]
    
    time_output = np.concatenate((time_input, time_cur), axis=None)
    signal_output = np.concatenate((signal_input, signal_cur), axis=None)
    
    return time_output, signal_output


if __name__ == '__main__':
    app_host = os.environ['app_host']
    app_port = int(os.environ['app_port'])
    app.run_server(debug=True
                   , port=app_port, host=app_host
                   )
