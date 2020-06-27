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
conn = psycopg2.connect( user = db_su, password = db_su_pwd,
                       , host = db_ip, port = db_port
                       , database = db_name)

# kafka
# https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1
from kafka import KafkaConsumer
from json import loads
# from pymongo import MongoClient
import numpy as np

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
for msg in consumer:
    message = msg.value
    topic   = message['topic']

    if topic not in topics:
        conn = create_table(conn, message)

    signal  = message['signal']
    signal  = np.array(signal.strip("[]").split(' '))
    if len(signal) == 7:
        continue
    else:
        message['signal'] = signal

    message = process_signal(message)
    conn    = insert_data(conn,message)
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
def create_measurement_table(conn, message)
    sql_create_table = """
        CREATE TABLE IF NOT EXISTS %s (
            segment_index int
          , P_s NUMERIC (12,4)
          , Q_s NUMERIC (12,4)
          , R_s NUMERIC (12,4)
          , S_s NUMERIC (12,4)
          , T_s NUMERIC (12,4)
          , patient_id
          , segment_start_time_s NUMERIC (12,4)
          , signal signal NUMERIC (16) []
          , metadata json
          );""" % topic
    cur = conn.cursor()
    cur.execute("""
    cur.execute(sql, (idx
      , segment_start_time_s, signal, message))
     """)

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
          , patient_id
          , segment_start_time_s NUMERIC (12,4)
          , signal signal NUMERIC (16) []
          , metadata json
          );""" % topic
    cur = conn.cursor()
    cur.execute("""
     ? (
      ,
      ,
      ,
      , topic text
      ,  text, reviewerName text, helpful text
      , metadata json NOT NULL
      ,


    reviewerText text, overall text, summary text, unixReviewerTime text, reviewTime text)
    ; """
    , topic,
    )
    conn.commit()
    return conn

conn    = insert_data(conn,message,message_next)


def insert_data(conn,message,message_next):
    topic       = message['topic']
    idx         = message['segment_meta']['index']
    time_pos    = message['time_pos']
    patient_id  = message['record_Meta']['name']
    start_time_s= message['segment_start_time_s']
    signal      = message['signal']

    message.pop('topic')
    message['segment_meta'].pop('index')
    message.pop('time_pos')
    message['record_Meta'].pop('name')
    message.pop('segment_start_time_s')
    message.pop('signal')

    sql_alter_prev = """
        INSERT INTO %s (segment_index, P_s, Q_s, R_s, S_s, T_s
          , segment_start_time_s, signal, metadata) VALUES (
            %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)
        ;""" % topic

    cur = conn.cursor()
    if message_next is not None:
        sql_insert = """
            INSERT INTO %s (segment_index, P_s, Q_s, R_s, S_s, T_s
              , segment_start_time_s, signal, metadata) VALUES (
                %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)
            ;""" % topic
        cur.execute(sql_insert, (idx
          , time_pos['P'], time_pos['Q'], time_pos['R'],
          , time_pos['S'], time_pos['T']
          , segment_start_time_s, signal, message))
    else:
        sql_insert = """
            INSERT INTO %s (segment_index,
              , segment_start_time_s, signal, metadata) VALUES (
                %%s, %%s, %%s, %%s)
            ;""" % topic
        cur.execute(sql, (idx
          , segment_start_time_s, signal, message))

    conn.commit()
    return conn


def process_signal(message):
