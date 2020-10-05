import sys
import os
import copy
import gc
import psycopg2
from psycopg2.extras import Json
from kafka import KafkaConsumer
from json import loads
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime

# Kafka consumer settings
kafka_bootstrap_server = sys.argv[1]
consumer_auto_offset_reset = "earliest"
consumer_enable_auto_commit = False
topic_pattern = sys.argv[3]

summary_table_name = 'measurements'


def main():
    conn = _create_postgres_conn()
    consumer = _create_kafka_consumer()
    
    the_current_time = datetime.now()
    current_time = the_current_time.strftime("%y-%m/%d, %H:%M:%S")
    print("    Current Time = " + str(current_time) + ' ')
    
    log_file.writelines('  Log time = ' + current_time + '\n')
    
    num_message = 0
    
    _create_measurements_table(conn, measurements_table_name)
    
    message_registry = dict()
    # msg is a message object from kafka (with all the kafka headers)
    # message = msg.value is readily deserialized into a dictionary
    for msg in consumer:
        log_string = _create_log_string(msg)
        log_header = _register_message(message_registry, msg, conn)
        log_string = log_header + log_string
        print(log_string)

        topic = msg.value['topic']
        message_index = msg.value['segment_meta']['index']
        
        # repeating message
        if log_header == 'Repeated: ':
            log_file.writelines(log_string)
            continue
            
        # preceding message exist in registry
        if message_index - 1 in message_registry[topic]:
            
            processed_message = _process_consecutive_messages(
                message_registry[topic],
                message_index - 1
            )
            
            _insert_data(conn, processed_message)
            
            message_registry[topic][message_index - 1]['processed'] = True
            
            if not is_message_needed(message_registry[topic], message_index-1):
                message_registry[topic][message_index - 1] = None

        # succeeding message exist in registry
        if message_index + 1 in message_registry[topic]:
            processed_message = _process_consecutive_messages(
                message_registry[topic],
                message_index
            )
            
            _insert_data(conn, processed_message)

            message_registry[topic][message_index]['processed'] = True
            
            if not is_message_needed(message_registry[topic], message_index):
                message_registry[topic][message_index - 1] = None

        # last message
        if log_header == 'Last: ':
            processed_message = _process_last_message(
                message_registry[topic],
                message_index
            )
    
            _insert_data(conn, processed_message)
    
    # len(messages_in_topic) should be the number of segments +1, when done.
        if len(message_registry[topic]) > idx - idx_neg:
            print(topic + ' is done.')
            log_file.writelines(topic + ' is done.')
            message_registry[topic] = {'Done': True}
            gc.collect()

        log_file.writelines(log_string)
        num_message += 1
        if num_message % 2000 == 0:
            the_current_time = datetime.now()
            current_time = the_current_time.strftime("%y-%m/%d, %H:%M:%S")
            print("    Current Time = " + str(current_time) + ' ')
            log_file.writelines('  Log time = ' + current_time + '='*25 + '\n')
            print('='*79)

    conn.close()
    
    
###############################################################################
# database operations
###############################################################################
def _create_summary_table(conn):
    sql_header = "CREATE TABLE IF NOT EXISTS %s " \
                 % summary_table_name
    
    sql_create_summary_table = sql_header + """
    (
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
        );
    """
    
    cur = conn.cursor()
    cur.execute(sql_create_summary_table)
    conn.commit()
    return


def _create_measurement_table(conn, current_message):
    topic = current_message['topic']
    number_of_segments = current_message['segment_meta']['index'] - \
        current_message['segment_meta']['index_neg']
    
    patient_id = current_message['record_Meta']['name']
    patient_age = current_message['subject_meta']['subject_age']
    target_HR = current_message['subject_meta']['target_HR']
    
    measurement_datetime = current_message['signal_meta']['window']
    sampling_frequency_Hz = current_message['signal_meta']['frequency_Hz']
    
    current_message.pop('topic')
    current_message.pop('segment_meta')
    current_message.pop('signal')
    current_message['record_Meta'].pop('name')
    current_message['subject_meta'].pop('subject_age')
    current_message['subject_meta'].pop('target_HR')
    current_message['signal_meta'].pop('window')
    current_message['signal_meta'].pop('frequency_Hz')
    
    sql_insert_into_summary = ("""
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
            """ + ', %%s' * 7 + ' );') % summary_table_name
    
    cur = conn.cursor()
    cur.execute(
        sql_insert_into_summary,
        (
            topic,
            number_of_segments,
            patient_id,
            patient_age,
            target_HR,
            measurement_datetime,
            sampling_frequency_Hz,
            Json(current_message)
        )
    )
    
    sql_create_measurement_table = """
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
        );""" % (topic, summary_table_name)
    
    cur.execute(sql_create_measurement_table)
    conn.commit()
    return


def _insert_data(conn, message):
    topic = message['topic']
    index = message['segment_meta']['index']
    
    patient_id = message['record_Meta']['name']
    measurement_datetime = message['signal_meta']['window']
    sampling_frequency_Hz = message['signal_meta']['frequency_Hz']
    segment_start_time_s = message['segment_start_time_s']
    segment_signal = message['signal']
    segment_signal = _convert_signal_postgres(segment_signal)
    
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
        time_interval = message['time_interval']
        message.pop('time_pos')
        message.pop('time_interval')
        
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
        cur.execute(
            sql_insert,
            (
                idx,
                time_pos['P'],
                time_pos['Q'],
                time_pos['R'],
                time_pos['S'],
                time_pos['T'],
                time_interval['PR'],
                time_interval['QRS'],
                time_interval['QT'],
                sampling_frequency_Hz,
                patient_id,
                measurement_datetime,
                topic,
                segment_start_time_s,
                segment_signal,
                Json(message)
            )
        )
    
    # last message
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
        
        cur.execute(
            sql_insert,
            (
                idx,
                sampling_frequency_Hz,
                patient_id,
                measurement_datetime,
                topic,
                segment_start_time_s,
                segment_signal,
                Json(message)
            )
        )
    conn.commit()
    return


###############################################################################
# msg processing
###############################################################################
def _register_message(message_registry, msg, conn):
    # get topic
    msg.value['topic'].replace('-', '_')
    topic = msg.value['topic']
    
    # msg is a message object from kafka (with all the kafka headers)
    # message = msg.value is readily deserialized into a dictionary
    message = msg.value
    message_index = message['segment_meta']['index']
    message_index_neg = message['segment_meta']['index_neg']
   
    # First message
    if topic not in message_registry:
        log_header = 'First: '
        message_registry[topic] = {'Done': False}
        
        _create_measurement_table(conn, copy.deepcopy(message))
        message_registry[topic][message_index] = \
            {'processed': False, 'message': message}
        
    # Repeating message
    elif message_registry[topic]['Done'] \
            or message_index in message_registry[topic]:
        log_header = 'Repeated: '
    
    # regular message
    elif message_index_neg < -1:
        log_header = ''
        message_registry[topic][message_index] = \
            {'processed': False, 'message': message}
        
    # last message
    else:
        log_header = 'Last: '
        message_registry[topic][message_index] = \
            {'processed': False, 'message': message}
        
    return log_header


def _process_consecutive_messages(messages_in_topic, index0):
    index1 = index0 + 1
    
    message0 = messages_in_topic[index0]['message']
    message1 = messages_in_topic[index1]['message']

    signal0 = message0['signal']
    signal0 = np.array(signal0.strip("[]").split(' '))
    signal1 = message1['signal']
    signal1 = np.array(signal1.strip("[]").split(' '))

    unit_time_s = 1 / message0['signal_meta']['frequency_Hz']
    time_pos = {'P': np.nan, 'Q': np.nan, 'R': np.nan,
                'S': np.nan, 'T': np.nan}
    
    # omit finding P, Q, S, and T
    if len(signal0) == 7 and len(signal1) == 7:
        time_pos['R'] = message1['segment_meta']['segment_start_time_s']
    
    # omit finding P and Q
    elif len(signal0) == 7 or index0 == 0:
        # signal0 was too long
        if len(signal0) == 7:
            message0['signal'] = message0['signal'].replace('...', 'np.nan')

        signal = signal1.astype(np.float)
        start_time_s = message1['segment_meta']['segment_start_time_s']

        R_loc = 0
        ptp_range = np.ptp(signal)
        R_next_loc = len(signal)
    
    # finding S
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        if pks_neg and pks_neg[pks_neg > R_loc]:
            S_loc = pks_neg[pks_neg > R_loc][0]
        else:
            S_loc = np.int(R_loc + 0.02 / unit_time_s)
    
    # finding T
        T_loc = np.nan
        T_limit = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
        T_seg = signal[S_loc:T_limit]
        
        if T_seg:
            ptp_range = np.ptp(T_seg)
            pks_T, prop = find_peaks(T_seg, prominence=0.02 * ptp_range)
            if pks_T:
                T_loc = pks_T[np.argmax(prop['prominences'])] + S_loc
        
        if isnan(T_loc):
            T_low_limit = np.int(0.2 * (R_next_loc - R_loc) + R_loc)
            T_loc = np.int(T_low_limit + 0.15 / unit_time_s)

        time_pos['R'] = start_time_s
        time_pos['S'] = start_time_s + S_loc * unit_time_s
        time_pos['T'] = start_time_s + T_loc * unit_time_s
        
    # omit finding S and T
    elif len(signal1) == 7 or idx_neg == -1:
        # signal1 was too long
        if len(signal1) == 7:
            message1['signal'] = message1['signal'].replace('...', 'np.nan')
        
        signal = signal1.astype(np.float)
        start_time_s = message0['segment_meta']['segment_start_time_s']
        
        ptp_range = np.ptp(signal)
        R_loc = len(signal)

    # finding Q
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        if pks_neg and pks_neg[pks_neg < R_loc]:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        else:
            Q_loc = np.int(R_loc - 0.02 / unit_time_s)

    # finding P
        P_loc = np.nan
        P_limit = np.int(0.5 * R_loc)
        P_seg = signal[P_limit:Q_loc]
        if P_seg:
            ptp_range = np.ptp(P_seg)
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            if pks_P:
                P_loc = pks_P[np.argmax(prop['prominences'])] + P_limit
        
        if isnan(P_loc):
            P_loc = np.int(Q_loc - 0.1 / unit_time_s)

        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s
    
    # omit finding None
    else:
        signal = np.concatenate((signal0, signal1), axis=0)
        signal = signal.astype(np.float)
        start_time_s = message0['segment_meta']['segment_start_time_s']
        
        ptp_range = np.ptp(signal)
        R_loc = len(signal0)
        R_next_loc = len(signal)

    # finding Q
        pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        if pks_neg and pks_neg[pks_neg < R_loc]:
            Q_loc = pks_neg[pks_neg < R_loc][-1]
        else:
            Q_loc = np.int(R_loc - 0.02 / unit_time_s)

    # finding P
        P_loc = np.nan
        P_limit = np.int(0.5 * R_loc)
        P_seg = signal[P_limit:Q_loc]
        if P_seg:
            ptp_range = np.ptp(P_seg)
            pks_P, prop = find_peaks(P_seg, prominence=0.01 * ptp_range)
            if pks_P:
                P_loc = pks_P[np.argmax(prop['prominences'])] + P_limit

        if isnan(P_loc):
            P_loc = np.int(Q_loc - 0.1 / unit_time_s)
    
    # finding S
    #     pks_neg, prop = find_peaks(-signal, prominence=0.02 * ptp_range)
        if pks_neg and pks_neg[pks_neg > R_loc]:
            S_loc = pks_neg[pks_neg > R_loc][0]
        else:
            S_loc = np.int(R_loc + 0.02 / unit_time_s)

    # finding T
        T_loc = np.nan
        T_limit = np.int(0.75 * (R_next_loc - R_loc) + R_loc)
        T_seg = signal[S_loc:T_limit]

        if T_seg:
            ptp_range = np.ptp(T_seg)
            pks_T, prop = find_peaks(T_seg, prominence=0.02 * ptp_range)
            if pks_T:
                T_loc = pks_T[np.argmax(prop['prominences'])] + S_loc

        if isnan(T_loc):
            T_low_limit = np.int(0.2 * (R_next_loc - R_loc) + R_loc)
            T_loc = np.int(T_low_limit + 0.15 / unit_time_s)

        time_pos['P'] = start_time_s + P_loc * unit_time_s
        time_pos['Q'] = start_time_s + Q_loc * unit_time_s
        time_pos['R'] = start_time_s + R_loc * unit_time_s
        time_pos['S'] = start_time_s + S_loc * unit_time_s
        time_pos['T'] = start_time_s + T_loc * unit_time_s
    # end finding P, Q, R, S, T
    
    time_interval = {
        'PR': time_pos['R'] - time_pos['P'],
        'QRS': time_pos['S'] - time_pos['Q'],
        'QT': time_pos['T'] - time_pos['Q']
    }

    message0['time_pos'] = time_pos
    message0['time_interval'] = time_interval
    message0['segment_start_time_s'] = \
        message0['segment_meta']['segment_start_time_s']
    message0['segment_meta'].pop('segment_start_time_s')
    
    return message0
    
    
def _process_last_message(messages_in_topic, index):
    last_message = messages_in_topic[index]['message']
    
    last_message['segment_start_time_s'] = \
        last_message['segment_meta']['segment_start_time_s']
    last_message['segment_meta'].pop('segment_start_time_s')
    
    return last_message
    
    
def is_message_needed(messages_in_topic, message_index):
    if not messages_in_topic[message_index]['processed']:
        return True
    
    if message_index == 0:
        return False
    
    previous_index = message_index - 1
    
    if previous_index not in messages_in_topic:
        return True
    
    if messages_in_topic[previous_index]['processed']:
        return False
    
    return True
    

###############################################################################
# private utility functions
###############################################################################
# Parse signal for postgres (str), and length of the signal (int).
def _convert_signal_postgres(signal):
    # Split the string containing signal into a list
    signal = signal \
        .strip("[]") \
        .replace('...', 'np.nan') \
        .split(" ")
    
    # note the length of the signal
    signal_length = len(signal)
    
    # join the list in to a string for postgres
    signal = "{" + ",".join(signal) + "}"
    
    return signal, signal_length


def _create_postgres_conn():
    # All parameters should be loaded by the wrapper shell script
    missing_variables = []
    for var in ['db_super_usr', 'db_su_pwd', 'psqlIp', 'psqlPort', 'dbName']:
        if var not in os.environ:
            missing_variables.append(var)
    
    if missing_environ:
        raise EnvironmentError("Failed because {} is not set.".format(var))
        pass
    
    # Creating a postgres connection using psycopg2
    conn = psycopg2.connect(
        user=os.environ['db_super_usr'],
        password=os.environ['db_su_pwd'],
        host=os.environ['psqlIp'],
        port=os.environ['psqlPort'],
        database=os.environ['dbName']
    )
    
    return conn


def _create_kafka_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers=kafka_bootstrap_server,
        auto_offset_reset=consumer_auto_offset_reset,
        enable_auto_commit=consumer_enable_auto_commit,
        value_deserializer=lambda x: loads(x.decode('utf-8'))
    )
    consumer.subscribe(pattern=topic_pattern)
    return consumer


def _create_log_string(msg):
    # msg is a message object from kafka (with all the kafka headers)
    # message = msg.value is readily deserialized into a dictionary
    message = msg.value
    
    output_string = \
        message['topic'] \
        + ': part: ' + str(msg.partition) \
        + ', offset: ' + str(msg.offset) \
        + ', idx: ' + str(message['segment_meta']['index'])
    
    return output_string


if __name__ == '__main__':
    log_file_path = sys.argv[2]
    log_file = open(log_file_path, 'a+', encoding='utf8', newline='')
    
    main()

    log_file.writelines('#' * 15 + str(current_time) + '#' * 15 + '\n')
    log_file.close()
