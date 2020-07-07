table_suffix = '_test07a'
'''
DY200706
'''
import sys
import os
import copy
import psycopg2
from psycopg2.extras import Json
from kafka import KafkaConsumer
from json import loads
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime

NaN = np.nan

bootstrapServer = sys.argv[1]  # 10.0.0.7:9092
log_file_path = sys.argv[2]
topic_pattern = sys.argv[3]


def main():
    print(table_suffix)
    print(table_suffix)
    print(table_suffix)
    
    db_ip = os.environ['psqlIp']
    db_port = os.environ['psqlPort']
    db_su = os.environ['db_super_usr']
    db_su_pwd = os.environ['db_su_pwd']
    db_name = os.environ['dbName']
    conn = psycopg2.connect(user=db_su, password=db_su_pwd
                            , host=db_ip, port=db_port
                            , database=db_name)
    
    consumer = KafkaConsumer(bootstrap_servers=bootstrapServer
                             , auto_offset_reset='earliest'
                             #                             , group_id='test_cons'
                             , enable_auto_commit=False
                             , value_deserializer=lambda x: loads(x.decode('utf-8')))
    consumer.subscribe(pattern=topic_pattern)
    
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time = " + str(current_time) + ' ')
    
    log_file = open(log_file_path, 'a+', encoding='utf8', newline='')
    log_file.writelines('Log time = ' + current_time + '\n')
    
    nMsg = 0
    topics = {}
    measurements_table_name = 'measurements' + table_suffix
    conn = create_measurements_table(conn, measurements_table_name)
    # msg is a message in kafka (with all the kafka headers)
    # message = msg.value is the byte-array from producers
    for msg in consumer:
        message = msg.value
        topic = message['topic']
        topic += table_suffix
        topic = topic.replace('-', '_')
        message['topic'] = topic
        idx = message['segment_meta']['index']
        idx_neg = message['segment_meta']['index_neg']
        
        if topic not in topics:
            conn = create_table(conn, copy.deepcopy(message), measurements_table_name)
            topics[topic] = {'Done': False}
    # Repeated Messages
        elif topics[topic]['Done'] or idx in topics[topic]:
            log_string = message['topic'] + '(REPEATED MESSAGE): part: ' + str(msg.partition) \
                         + ', offset: ' + str(msg.offset) \
                         + ', idx: ' + str(message['segment_meta']['index'])
            print(log_string)
            log_file.writelines(log_string)
            continue
        
        topics[topic][idx] = {'processed': False, 'message': message}
        if idx - 1 in topics[topic]:
            log_string = topic + ': part: ' + str(msg.partition) \
                         + ', offset: ' + str(msg.offset) \
                         + ', idx: ' + str(message['segment_meta']['index'])
            print(log_string)
            
            message_prev = process_signal(topics[topic][idx - 1]['message']
                                          , topics[topic][idx]['message'])
            message_prev['signal'], len_sig = convert_signal(message_prev['signal'])
            conn = insert_data(conn, message_prev, measurements_table_name)
            log_file.writelines(log_string)
            
            topics[topic][idx - 1]['processed'] = True
            if idx - 2 in topics[topic] and topics[topic][idx - 2]['processed']:
                topics[topic][idx - 1]['message'] = None
        
        if idx + 1 in topics[topic]:
            log_string = topic + ': part: ' + str(msg.partition) \
                         + ', offset: UNKNOWN' + ', idx: ' \
                         + str(topics[topic][idx]['message']['segment_meta']['index'])
            print(log_string)
            
            message_proc = process_signal(topics[topic][idx]['message']
                                          , topics[topic][idx + 1]['message'])
            message_proc['signal'], len_sig = convert_signal(message_proc['signal'])
            conn = insert_data(conn, message_proc, measurements_table_name)
            log_file.writelines(log_string)
            
            topics[topic][idx]['processed'] = True
            if idx == 0:
                topics[topic][idx]['message'] = None
            
            if topics[topic][idx + 1]['processed']:
                topics[topic][idx + 1]['message'] = None
        
        if idx_neg == -1:
            log_string = topic + ' : part: ' + str(msg.partition) \
                         + ', offset: ' + str(msg.offset) \
                         + ', idx: ' + '-1' \
                         + ', len: ' + str(len_sig) + '\n'
            
            print(log_string)
            
            message = process_signal_last(topics[topic][idx]['message'])
            message['signal'], len_sig = convert_signal(message['signal'])
            conn = insert_data(conn, message, measurements_table_name)
            
            log_file.writelines(log_string)
        
        if len(topics[topic]) > idx - idx_neg:
            print(topic + ' is done.')
            topics[topic] = {'Done': True}
        
        nMsg += 1
        if nMsg % 2000 == 0:
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current Time = " + str(current_time) + ' ')
            log_file.writelines('Log time = ' + current_time + '===================================\n')
            print('================================================================================')
    
    conn.close()
    log_file.writelines('#################' + str(current_time) + '##################################################')
    log_file.close()


################################################################################
def create_measurements_table(conn, summary_table):
    sql_create_measurements_table = """
        DROP TABLE IF EXISTS %s;
        CREATE TABLE %s (
              topic VARCHAR (32) PRIMARY KEY
            , patient_id VARCHAR (32)
            , patient_age NUMERIC (6,3)
            , target_HR NUMERIC (6,3)
            , measurement_datetime VARCHAR (32)
            , number_of_segments INT
            , PR_s NUMERIC (6,4)
            , PR_s_dist NUMERIC (6,4) []
            , QRS_s NUMERIC (6,4)
            , QRS_dist NUMERIC (6,4) []
            , QT_s NUMERIC (6,4)
            , QT_dist NUMERIC (6,4) []
            , sampling_frequency_Hz NUMERIC (6,2)
            , signal_length_s NUMERIC (12,4)
            , signal_whole NUMERIC (16) []
            , metadata JSON
        );""" % (summary_table, summary_table)
    
    # sql_create_measurements_table = """
    #     CREATE TABLE IF NOT EXISTS %s (
    #           topic VARCHAR (32) PRIMARY KEY
    #         , patient_id VARCHAR (32)
    #         , patient_age NUMERIC (6,3)
    #         , target_HR NUMERIC (6,3)
    #         , measurement_datetime VARCHAR (32)
    #         , number_of_segments INT
    #         , PR_s NUMERIC (6,4)
    #         , PR_s_dist NUMERIC (6,4) []
    #         , QRS_s NUMERIC (6,4)
    #         , QRS_dist NUMERIC (6,4) []
    #         , QT_s NUMERIC (6,4)
    #         , QT_dist NUMERIC (6,4) []
    #         , sampling_frequency_Hz NUMERIC (6,2)
    #         , signal_length_s NUMERIC (12,4)
    #         , signal_whole NUMERIC (16) []
    #         , metadata JSON
    #     );""" % (summary_table)
    
    cur = conn.cursor()
    cur.execute(sql_create_measurements_table)
    conn.commit()
    return conn


def create_table(conn, message, summary_table):
    topic = message['topic']
    number_of_segments = message['segment_meta']['index'] - message['segment_meta']['index_neg']
    patient_id = message['record_Meta']['name']
    patient_age = message['subject_meta']['subject_age']
    target_HR = message['subject_meta']['target_HR']
    measurement_datetime = message['signal_meta']['window']
    sampling_frequency_Hz = message['signal_meta']['frequency_Hz']
    
    local_msg = message
    local_msg.pop('topic')
    local_msg.pop('segment_meta')
    local_msg.pop('signal')
    local_msg['record_Meta'].pop('name')
    local_msg['subject_meta'].pop('subject_age')
    local_msg['subject_meta'].pop('target_HR')
    local_msg['signal_meta'].pop('window')
    local_msg['signal_meta'].pop('frequency_Hz')
    
    sql_insert_measurements = ("""
        INSERT INTO %s (
              topic
            , number_of_segments
            , patient_id
            , patient_age
            , target_HR
            , measurement_datetime
            , sampling_frequency_Hz
            , metadata
            ) VALUES ( %%s
            """ + ', %%s' * 7 + ' );') % summary_table
    cur = conn.cursor()
    cur.execute(sql_insert_measurements, (topic
                                          , number_of_segments
                                          , patient_id
                                          , patient_age
                                          , target_HR
                                          , measurement_datetime
                                          , sampling_frequency_Hz
                                          , Json(local_msg)
                                          ))
    
    sql_create_table = """
        DROP TABLE IF EXISTS %s;
        CREATE TABLE %s (
            segment_index INT
          , P_s NUMERIC (12,4)
          , Q_s NUMERIC (12,4)
          , R_s NUMERIC (12,4)
          , S_s NUMERIC (12,4)
          , T_s NUMERIC (12,4)
          , PR_s NUMERIC (6,4)
          , QRS_s NUMERIC (6,4)
          , QT_s  NUMERIC (6,4)
          , fs_Hz NUMERIC (6,2)
          , patient_id VARCHAR (32)
          , measurement_datetime VARCHAR (32)
          , topic VARCHAR (32)
          , segment_start_time_s NUMERIC (12,4)
          , signal NUMERIC (16) []
          , metadata JSON
          , PRIMARY KEY (segment_index)
          , FOREIGN KEY (topic) REFERENCES %s (topic)
        );""" % (topic, topic, summary_table)
    cur.execute(sql_create_table)
    conn.commit()
    return conn


def insert_data(conn, message, summary_table):
    topic = message['topic']
    idx = message['segment_meta']['index']
    
    patient_id = message['record_Meta']['name']
    measurement_datetime = message['signal_meta']['window']
    sampling_frequency_Hz = message['signal_meta']['frequency_Hz']
    segment_start_time_s = message['segment_start_time_s']
    segment_signal = message['signal']
    
    message.pop('topic')
    message['segment_meta'].pop('index')
    message['record_Meta'].pop('name')
    message['signal_meta'].pop('window')
    message['signal_meta'].pop('frequency_Hz')
    message.pop('segment_start_time_s')
    message.pop('signal')
    
    cur = conn.cursor()
    if message['segment_meta']['index_neg'] != -1:
        time_pos = message['time_pos']
        time_intvl = message['time_intvl']
        message.pop('time_pos')
        message.pop('time_intvl')
        
        sql_insert = ("""
            INSERT INTO %s (
                  segment_index
                , P_s
                , Q_s
                , R_s
                , S_s
                , T_s
                , PR_s
                , QRS_s
                , QT_s
                , fs_Hz
                , patient_id
                , measurement_datetime
                , topic
                , segment_start_time_s
                , signal
                , metadata
            ) VALUES ( %%s
            """ + ', %%s' * 15 + ' );') % topic
        cur.execute(sql_insert, (idx
                                 , time_pos['P']
                                 , time_pos['Q']
                                 , time_pos['R']
                                 , time_pos['S']
                                 , time_pos['T']
                                 , time_intvl['PR']
                                 , time_intvl['QRS']
                                 , time_intvl['QT']
                                 , sampling_frequency_Hz
                                 , patient_id
                                 , measurement_datetime
                                 , topic
                                 , segment_start_time_s
                                 , segment_signal
                                 , Json(message)
                                 ))
    else:
        sql_insert = ("""
            INSERT INTO %s (
                  segment_index
                , fs_Hz
                , patient_id
                , measurement_datetime
                , topic
                , segment_start_time_s
                , signal
                , metadata
            ) VALUES ( %%s
            """ + ', %%s' * 7 + ' );') % topic
        
        cur.execute(sql_insert, (idx
                                 , sampling_frequency_Hz
                                 , patient_id
                                 , measurement_datetime
                                 , topic
                                 , segment_start_time_s
                                 , segment_signal
                                 , Json(message)
                                 ))
    
    # if idx == 0:
    #     patient_age = message['subject_meta']['subject_age']
    #     target_HR   = message['subject_meta']['target_HR']
    #     message['subject_meta'].pop('subject_age')
    #     message['subject_meta'].pop('target_HR')
    #
    #     sql_insert_measurements = ("""
    #         INSERT INTO %s (
    #               topic
    #             , patient_id
    #             , patient_age
    #             , target_HR
    #             , measurement_datetime
    #             , sampling_frequency_Hz
    #             , metadata
    #         ) VALUES ( %%s
    #         """ + ', %%s'*6 + ' );') % summary_table
    #
    #     cur.execute(sql_insert_measurements,  ( topic
    #                                           , patient_id
    #                                           , patient_age
    #                                           , target_HR
    #                                           , measurement_datetime
    #                                           , sampling_frequency_Hz
    #                                           , Json(message)
    #                                           ))
    
    conn.commit()
    return conn


def process_signal(message_curr, message_next) -> 'processed message':
    idx = message_curr['segment_meta']['index']
    idx_next = message_next['segment_meta']['index']
    if idx_next - idx != 1:
        return None
    
    idx_neg = message_next['segment_meta']['index_neg']
    sig_a = message_curr['signal']
    sig_a = np.array(sig_a.strip("[]").split(' '))
    sig_b = message_next['signal']
    sig_b = np.array(sig_b.strip("[]").split(' '))
    
    unit_time_s = 1 / message_curr['signal_meta']['frequency_Hz']
    start_time_s = message_curr['segment_meta']['segment_start_time_s']
    
    if len(sig_a) == 7 and len(sig_b) == 7:
        time_pos = {'P': NaN, 'Q': NaN, 'R': NaN
            , 'S': NaN, 'T': NaN}
        time_intvl = {'PR': NaN, 'QRS': NaN, 'QT': NaN}
    
    elif len(sig_a) == 7 or idx == 0:
        if len(sig_a) == 7:
            message_curr['signal'] = message_curr['signal'].replace('...', 'NaN')
        signal = sig_b.astype(np.float)
        time_pos = {'P': NaN, 'Q': NaN, 'R': 0
            , 'S': 0, 'T': 0}
        time_intvl = {'PR': NaN, 'QRS': NaN, 'QT': NaN}
        
        ptp_range = np.ptp(signal)
        R_loc = 0
        R_next_loc = len(signal)
        
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        try:
            S_loc = pks_neg[pks_neg > R_loc][0]
        except:
            S_loc = np.int(R_loc + 0.02 / unit_time_s)
        
        try:
            T_limit = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
            T_seg = signal[S_loc:T_limit]
            ptp_range = np.ptp(T_seg)
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
        time_pos = {'P': 0, 'Q': 0, 'R': 0
            , 'S': NaN, 'T': NaN}
        time_intvl = {'PR': 0, 'QRS': NaN, 'QT': NaN}
        
        ptp_range = np.ptp(signal)
        R_loc = len(sig_a)
        
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        try:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        except:
            Q_loc = np.int(R_loc - 0.02 / unit_time_s)
        
        try:
            P_limit = np.int(0.5 * R_loc)
            P_seg = signal[P_limit:Q_loc]
            ptp_range = np.ptp(P_seg)
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            P_loc = pks_P[np.argmax(prop['prominences'])] + P_limit
        except:
            P_loc = np.int(Q_loc - 0.1 / unit_time_s)
        
        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s
        
        time_intvl['PR'] = time_pos['R'] - time_pos['P']
    
    else:
        signal = np.concatenate((sig_a, sig_b), axis=0)
        signal = signal.astype(np.float)
        time_pos = {'P': 0, 'Q': 0, 'R': 0
            , 'S': 0, 'T': 0}
        time_intvl = {'PR': 0, 'QRS': 0, 'QT': 0}
        
        ptp_range = np.ptp(signal)
        R_loc = len(sig_a)
        R_next_loc = len(signal)
        
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        try:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        except:
            Q_loc = np.int(R_loc - 0.02 / unit_time_s)
        
        try:
            S_loc = pks_neg[pks_neg > R_loc][0]
        except:
            S_loc = np.int(R_loc + 0.02 / unit_time_s)
        
        try:
            T_limit = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
            T_seg = signal[S_loc:T_limit]
            ptp_range = np.ptp(T_seg)
            pks_T, prop = find_peaks(T_seg, prominence=0.02 * ptp_range)
            T_loc = pks_T[np.argmax(prop['prominences'])] + S_loc
        except:
            T_low_limit = np.int(0.2 * (R_next_loc - R_loc) + R_loc)
            T_loc = np.int(T_low_limit + 0.15 / unit_time_s)
        
        try:
            P_limit = np.int(0.6 * R_loc)
            P_seg = signal[P_limit:Q_loc]
            ptp_range = np.ptp(P_seg)
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            P_loc = pks_P[np.argmax(prop['prominences'])] + P_limit
        except:
            P_loc = np.int(Q_loc - 0.1 / unit_time_s)
        
        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s
        time_pos['S'] = start_time_s + S_loc * unit_time_s
        time_pos['T'] = start_time_s + T_loc * unit_time_s
        
        time_intvl['PR'] = time_pos['R'] - time_pos['P']
        time_intvl['QRS'] = time_pos['S'] - time_pos['R']
        time_intvl['QT'] = time_pos['T'] - time_pos['Q']
    
    message_curr['time_pos'] = time_pos
    message_curr['time_intvl'] = time_intvl
    message_curr['segment_start_time_s'] = message_curr['segment_meta']['segment_start_time_s']
    message_curr['segment_meta'].pop('segment_start_time_s')
    return message_curr


def process_signal_last(message):
    message['segment_start_time_s'] = message['segment_meta']['segment_start_time_s']
    message['segment_meta'].pop('segment_start_time_s')
    return message


def convert_signal(signal) -> 'parse signal for postgres and length: str, int':
    signal = signal.strip("[]").replace('...', 'NaN').split(" ")
    len_sig = len(signal)
    signal = "{" + ",".join(signal) + "}"
    return signal, len_sig


if __name__ == '__main__':
    main()
