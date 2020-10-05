import sys
import numpy as np
import boto3
from kafka import KafkaProducer
import time
import json

bucket_name = sys.argv[1]
file_name_format = sys.argv[2]
bootstrap_servers = sys.argv[3]
topic_ids = sys.argv[4]


def main():
    # parse topic_ids
    topic_indices = _parse_topic_indices(topic_ids)
    
    s3 = boto3.resource('s3')
    
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                             acks=1, linger_ms=10,
                             batch_size=786432)
    print(bootstrap_servers)
    
    num_of_messages = 0
    lines = {}
    topic_offsets = [None] * 8000  # there will be upto 8000 topics
    is_topic_produced = [False] * 8000
    fileName_idx_min_width = 6
    is_message_production_started = False
    
    while True:
        line_idx_neg_check = 0
        for topic_idx in topic_indices:
            if topic_offsets[topic_idx] is None:
                
                # get fileName
                file_name = file_name_format.format(
                    idx_str=str(topic_idx).zfill(fileName_idx_min_width)
                )
                s3_obj = s3.Object(bucket_name, file_name)
                print(bucket_name, '/', file_name)
                
                # read files from s3
                obj_body = s3_obj.get()['Body'].read().decode('utf-8')
                lines[topic_idx] = obj_body.split('\n')
                topic_offsets[topic_idx] = -1
            
            elif is_topic_produced[topic_idx] is False:
                # produce messages to each topic
                topic_offsets[topic_idx] += 1
                
                line = lines[topic_idx][topic_offsets[topic_idx]]
                line_obj = json.loads(line)
                topic = line_obj['topic']
                
                producer.send(topic, value=line.encode('utf-8'))
                
                num_of_messages += 1
                is_message_production_started = True
                line_idx_neg = int(line_obj['segment_meta']['index_neg'])
                
                if line_idx_neg == -1:
                    TopicAllProduced[topic_idx] = True
                
                # Sleep for 1 ms after every 500 messages produced.
                if nMsg % 500 == 0:
                    time.sleep(0.001)
                
                if line_idx_neg < line_idx_neg_check:
                    line_idx_neg_check = line_idx_neg
            
        # end for
        
        if is_message_production_started:
            print('At most ' + str(-line_idx_neg_check - 1) +
                  ' messages per topic left to produce.')
            
        # Break the while loop, if no more messages to produce
            if line_idx_neg_check == -1:
                break
    
    producer.flush()
    print(str(nMsg) + ' lines produced.')


###############################################################################
# private utility functions
###############################################################################
def _parse_topic_indices(ids):
    arguments = list(map(int, ids.split('..')))
    
    if len(arguments) == 1:
        topic_indices = \
            np.arange(0, arguments[0])
    
    elif len(arguments) == 2:
        topic_indices = \
            np.arange(arguments[0], arguments[1] + 1)
    
    else:
        topic_indices = \
            np.arange(arguments[0], arguments[2] + 1, arguments[1])
    
    return topic_indices


if __name__ == '__main__':
    main()
