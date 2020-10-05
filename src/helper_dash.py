# helper_dash.py
import time
import psycopg2
from psycopg2 import errors

def get_metadata(conn, topic, table_suffix):
    sql_get_metadata = ("""
        SELECT
            number_of_segments
          , patient_id
          , patient_age
          , target_HR
          , measurement_datetime
          , sampling_frequency_Hz
        FROM
            % s
        WHERE
            topic = '%s'
    """) % ('measurements' + table_suffix, topic)
    
    t = 0
    cur = conn.cursor()
    while True:
        try:
            cur.execute(sql_get_metadata)
            metadata_tuple = cur.fetchall()[0]
        except:
            t += 1
            time.sleep(0.1)
            print('getMetadata: waiting... ' + str(0.1 * t) + 's.')
            continue
        break
    
    metadata_dict = {
        'number_of_segments': int(metadata_tuple[0]),
        'patient_id': metadata_tuple[1],
        'patient_age': float(metadata_tuple[2]),
        'target_HR': float(metadata_tuple[3]),
        'measurement_datetime': metadata_tuple[4],
        'fs_Hz': float(metadata_tuple[5])
    }
    
    # ensuring everything commits on the injection side
    time.sleep(0.001)
    return metadata_dict


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
