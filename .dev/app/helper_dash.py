# helper_dash.py
import time
def getMetadata(conn, topic, table_suffix):
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
    
    metadata_dict = {'number_of_segments': int(metadata_tuple[0])
        , 'patient_id': metadata_tuple[1]
        , 'patient_age': float(metadata_tuple[2])
        , 'target_HR': float(metadata_tuple[3])
        , 'measurement_datetime': metadata_tuple[4]
        , 'fs_Hz': float(metadata_tuple[5])
                     }
    time.sleep(0.001)  # to ensure everything commits on the injection side
    return metadata_dict

