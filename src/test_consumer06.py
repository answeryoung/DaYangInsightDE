table_suffix = '_test06a'

import sys
bootstrapServer = sys.argv[1]  #10.0.0.7:9092
log_file_path   = sys.argv[2]
topic_pattern   = sys.argv[3]

import os
import psycopg2
db_ip      = os.environ['psqlIp']
db_port    = os.environ['psqlPort']
db_su      = os.environ['db_super_usr']
db_su_pwd  = os.environ['db_su_pwd']
db_db_name = os.environ['dbName']
conn = psycopg2.connect( user = db_su, password = db_su_pwd
                       , host = db_ip, port = db_port
                       , database = db_name)

# kafka
# https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1
from kafka import KafkaConsumer
from json import loads
# from pymongo import MongoClient
import numpy as np
import math
from scipy.signal import find_peaks

consumer = KafkaConsumer( bootstrap_servers=bootstrapServer
                        , auto_offset_reset='earliest'
#                         , group_id='test_cons'
                        , enable_auto_commit=False
, value_deserializer=lambda x: loads(x.decode('utf-8')))

consumer.subscribe(pattern=topic_pattern)

# client     = MongoClient('localhost:27017')
# collection = client.test03.test03

from datetime import datetime
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)


log_file= open(log_file_path, 'a+', encoding='utf8', newline = '')
log_file.writelines('Log time = ' + current_time)

nMsg    = 0
topics  = {}
conn    = create_measurements_table(conn, table_suffix)
for msg in consumer:
    message = msg.value
    message['topic'] += table_suffix
    topic   = message['topic']

    if topic not in topics:
        conn    = create_table(conn, message)
        topics[topic]   = None

    if message['segment_meta']['index'] == 0:
        topics[topic]   = message
        topic       = create_table(conn, message)
        continue
    
    message_prev    = process_signal(topics[topic], message)
    conn            = insert_data(conn, table_suffix, message_prev)
    
    
    if message['segment_meta']['idx_neg'] == -1:
        conn        = insert_data(conn, table_suffix, message)
    
    topics[topic] = message
    log_string = message['topic'] + ' : part: ' + str(msg.partition)
            + ', offset: ' + str(msg.offset)
            + ', idx: ' + str(i)
            + ', len: ' + str(a.size)
    print(log_string)
    log_file.writelines(log_string)
    
    nMsg += 1
    if nMsg % 2000 == 0:
        print('================================================================================')


conn.close()
log_file.writelines('################################################################################')
log_file.close()

################################################################################
def create_measurements_table(conn, table_suffix):
    table_name = 'measurements' + table_suffix
    sql_create_measurements_table = """
        CREATE TABLE IF NOT EXISTS %s (
          , patient_id varchar(32)
          , measurement_datetime varchar(32)
          , PR_s NUMERIC (6,4)
          , PR_s_dist NUMERIC (6,4) []
          , QRS_s NUMERIC (6,4)
          , QRS_dist NUMERIC (6,4) []
          , QT_s NUMERIC (6,4)
          , QT_dist NUMERIC (6,4) []
          , signal_length_s NUMERIC (12,4)
          , signal_whole NUMERIC (16) []
          , metadata json
        );""" % table_name
    cur = conn.cursor()
    cur.execute(sql_create_measurements_table)
    conn.commit()
    return conn

def create_table(conn, message):
    topic = message['topic']
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS %s (
            segment_index int
          , P_s NUMERIC (12,4)
          , Q_s NUMERIC (12,4)
          , R_s NUMERIC (12,4)
          , S_s NUMERIC (12,4)
          , T_s NUMERIC (12,4)
          , PR_s NUMERIC (6,4)
          , QRS_s NUMERIC (6,4)
          , QT_s NUMERIC (6,4)
          , patient_id varchar(32)
          , measurement_datetime varchar(32)
          , segment_start_time_s NUMERIC (12,4)
          , signal NUMERIC (16) []
          , metadata json
        );""" % topic
    cur = conn.cursor()
    cur.execute(sql_create_table)
    conn.commit()
    return conn

def insert_data(conn, table_suffix, message):
    measurements_table_name = 'measurements' + table_suffix
    topic       = message['topic']
    idx         = message['segment_meta']['index']
    
    patient_id  = message['record_Meta']['name']
    measurement_datetime = message['signal_meta']['window']
    segment_start_time_s = message['segment_start_time_s']
    segment_signal       = message['signal']

    message.pop('topic')
    message['segment_meta'].pop('index')
    message['record_Meta'].pop('name')
    message['signal_meta'].pop('window')
    message.pop('segment_start_time_s')
    message.pop('signal')
    
    cur = conn.cursor()
    if message['segment_meta']['idx_neg'] != -1:
        time_pos = message['time_pos']
        time_intvl = message['time_pos']
        message.pop('time_pos')
        message.pop('time_intvl')
        sql_insert = """
            INSERT INTO %s (
                segment_index
              , P_s, Q_s, R_s, S_s, T_s, PR_s, QRS_s, QT_s
              , patient_id, measurement_datetime
              , segment_start_time_s, signal, metadata
            ) VALUES (
                %%s
              , %%s, %%s, %%s
              , %%s, %%s
              , %%s, %%s, %%s
              , %%s, %%s
              , %%s, %%s, %%s
            );""" % topic
        cur.execute(sql_insert, (idx
          , time_pos['P'], time_pos['Q'], time_pos['R']
          , time_pos['S'], time_pos['T']
          , time_intvl['PR'], time_intvl['QRS'], time_intvl['QT']
          , patient_id, measurement_datetime
          , segment_start_time_s, segment_signal, message))
    else:
        sql_insert = """
            INSERT INTO %s (
                segment_index,
              , patient_id, measurement_datetime
              , segment_start_time_s, signal, metadata
            ) VALUES (
                %%s
              , %%s, %%s
              , %%s, %%s, %%s
            );""" % topic
        cur.execute(sql_insert, (idx
          , patient_id, measurement_datetime
          , segment_start_time_s, segment_signal, message))
        
    if idx == 0:
        sql_insert_measurements = """
            INSERT INTO measurements %s (
                patient_id, measurement_datetime, metadata
            ) VALUES (
                %%s, %%s, %%s
            );""" % measurements_table_name
        cur.execute(sql_insert, (
            patient_id, measurement_datetime, message))
            
    conn.commit()
    return conn


def process_signal(message,message_next):
    idx     = message['segment_meta']['index']
    idx_neg = message_next['segment_meta']['index_neg']
    sig_a = message['signal']
    sig_a = np.array(sig_a.strip("[]").split(' '))
    sig_b = message_next['signal']
    sig_b = np.array(sig_b.strip("[]").split(' '))
    
    unit_time_s = 1/message['signal_meta']['frequency_Hz']
    start_time_s= message['segment_meta']['segment_start_time_s']
    
    if len(sig_a) == 7 and len(sig_b) == 7:
        time_pos    = { 'P': np.nan, 'Q': np.nan, 'R': np.nan
                      , 'S': np.nan, 'T': np.nan}
        time_intvl  = { 'PR': np.nan, 'QRS': np.nan, 'QT': np.nan}
        
    elif len(sig_a) == 7 or idx == 0:
        signal = sig_b.astype(np.float)
        time_pos    = { 'P': np.nan, 'Q': np.nan, 'R': 0
                      , 'S': 0, 'T': 0 }
        time_intvl  = { 'PR': np.nan, 'QRS': np.nan, 'QT': np.nan}

        
        
        ptp_range = np.ptp(signal)
        R_loc     = 0
        R_next_loc    = len(signal)

        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        try:
            S_loc = pks_neg[pks_neg > R_loc][0]
        except:
            S_loc = np.int(R_loc + 0.02 / unit_time_s)

        T_limit   = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
        T_seg     = sig_ab[S_loc:T_limit]
        ptp_range = np.ptp(T_seg)
        try:
            pks_T, prop = find_peaks(T_seg, prominence=0.02 * ptp_range)
            T_loc = pks_T[np.argmax(prop['prominences'])] + S_loc
        except:
            T_low_limit = np.int(0.2 * (R_next_loc - R_loc) + R_loc)
            T_loc = np.int(T_low_limit + 0.15 / unit_time_s)

        time_pos['R'] = message_next['segment_meta']['segment_start_time_s']
        time_pos['S'] = time_pos['R'] + S_loc * unit_time_s
        time_pos['T'] = time_pos['R'] + T_loc * unit_time_s
   
        
    
    elif len(sig_b) == 7 or idx_neg == -1:
        signal = sig_a.astype(np.float)
        time_pos    = { 'P': 0, 'Q': 0, 'R': 0
                      , 'S': np.nan, 'T': np.nan}
        time_intvl  = { 'PR': 0, 'QRS': np.nan, 'QT': np.nan}

        ptp_range   = np.ptp(signal)
        R_loc       = len(sig_a)

        pks_neg, prop   = find_peaks(-sig_ab, prominence=0.02 * ptp_range)
        try:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        except:
            Q_loc = np.int(R_loc - 0.02 / unit_time_s)

        P_limit = np.int(0.5 * R_loc)
        P_seg   = sig_ab[P_limit:Q_loc]
        ptp_range = np.ptp(P_seg)
        try:
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            P_loc = pks_P[np.argmax(prop['prominences'])] + P_limit
        except:
            P_loc = np.int(Q_loc - 0.1 / unit_time_s)

        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s

        time_intvl['PR']  = time_pos['R'] - time_pos['P']
        
    else:
        signal = np.concatenate((sig_a, sig_b), axis=0)
        signal = signal.astype(np.float)
        time_pos = {'P': 0, 'Q': 0, 'R': 0
            , 'S': 0, 'T': 0}
        time_intvl = {'PR': 0, 'QRS': 0, 'QT': 0}

        ptp_range   = np.ptp(signal)
        R_loc       = len(signal)
        R_next_loc  = len(signal)

        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        try:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        except:
            Q_loc = np.int(R_loc - 0.02/unit_time_s)
        
        try:
            S_loc = pks_neg[pks_neg > R_loc][0]
        except:
            S_loc = np.int(R_loc + 0.02/unit_time_s)
    
        
        T_limit     = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
        T_seg       = signal[S_loc:T_limit]
        ptp_range   = np.ptp(T_seg)
        try:
            pks_T, prop = find_peaks(T_seg, prominence=0.02 * ptp_range)
            T_loc   = pks_T[np.argmax(prop['prominences'])] + S_loc
        except:
            T_low_limit = np.int(0.2 * (R_next_loc - R_loc) + R_loc)
            T_loc       = np.int(T_low_limit + 0.15/unit_time_s)

        P_limit     = np.int(0.5 * R_loc)
        P_seg       = signal[P_limit:Q_loc]
        ptp_range   = np.ptp(P_seg)
        try:
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            P_loc   = pks_P[np.argmax(prop['prominences'])]+P_limit
        except:
            P_loc   = np.int(Q_loc - 0.1 / unit_time_s)

        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s
        time_pos['S'] = start_time_s + S_loc * unit_time_s
        time_pos['T'] = start_time_s + T_loc * unit_time_s

        time_intvl['PR']  = time_pos['R'] - time_pos['P']
        time_intvl['QRS'] = time_pos['S'] - time_pos['R']
        time_intvl['QT']  = time_pos['T'] - time_pos['Q']
        
    message['time_pos'] = time_pos
    message['time_pos'] = time_intvl
    return message
