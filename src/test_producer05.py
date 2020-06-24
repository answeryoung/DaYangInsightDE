import sys

bucketName        = sys.argv[1]
fileName_fmt      = sys.argv[2]
bootstrapServer   = sys.argv[3]
topic_ids         = sys.argv[4]

import numpy as np
topic_idx_param = list(map(int, topic_ids.split('..')))
if len(topic_idx_param) == 1:
    topic_ids   = np.arange(0, topic_idx_param[0])
elif len(topic_idx_param) == 2:
    topic_ids   = np.arange( topic_idx_param[0], topic_idx_param[1] + 1)
elif len(topic_idx_param) == 3:
    topic_ids   = np.arange( topic_idx_param[0], topic_idx_param[2]+ 1
                           , topic_idx_param[1])

# Create topics
# from kafka.admin import KafkaAdminClient, NewTopic
# admin_client = KafkaAdminClient(
#     bootstrap_servers=bootstrapServer,
#     client_id='test'
# )

# topic_list = []
# topic_list.append(NewTopic(name=Topic, num_partitions=4, replication_factor=2))
# admin_client.create_topics(new_topics=topic_list, validate_only=False)
# print(Topic': topic has been created')


# read file from s3
import boto3
s3    = boto3.resource('s3')
# obj   = s3.Object(bucketName,fileName)
# body  = obj.get()['Body'].read().decode('utf-8')
# lines = body.split('\n')
# print(fileName)
# print('Topic: '+Topic)
# produce messages
# dd = np.array(d["signal"].strip("[]").split(","))
# produce

from kafka import KafkaProducer
producer = KafkaProducer( bootstrap_servers=bootstrapServer
                        , acks = 1, linger_ms = 10
                        , batch_size = 786432)
print(bootstrapServer)

import time
import json


nLine = 0
obj = {}
lines = {}

nMsg    = 0
TopicOffsets = [None] * 8000 # there will be upto 8000 topics
TopicAllProduced = [False] * 8000
fileName_idx_min_width = 6
fileName_idx_filler    = "0"

while True:
    line_idx_neg_check = -1

    for topic_idx in topic_ids:
        if TopicOffsets[topic_idx] is None:
# get fileName
            fileName  = fileName_fmt.format(idx_str = str(topic_idx).zfill(6))
            s3_obj    = s3.Object(bucketName,fileName)
            obj_body  = s3_obj.get()['Body'].read().decode('utf-8')
            lines[topic_idx] = obj_body.split('\n')

# produce the first line, corresponding topic will be created automaticly
            TopicOffsets[topic_idx] = 0
            line       = lines[topic_idx][TopicOffsets[topic_idx]]
            line_dict  = json.loads(line)
            Topic      = line_dict['topic']
            producer.send(Topic, value=line.encode('utf-8'))
            nMsg += 1
            line_idx_neg = int(line_dict['segment_meta']['index_neg'])
            producer.flush()
            time.sleep(0.01)
            print(Topic+' Created')
        elif TopicAllProduced[topic_idx] is False:
# produce more messages to each topic
            TopicOffsets[topic_idx] += 1
            line       = lines[topic_idx][TopicOffsets[topic_idx]]
            line_dict  = json.loads(line)
            Topic      = line_dict['topic']
            producer.send(Topic, value=line.encode('utf-8'))
            nMsg += 1
            line_idx_neg = int(line_dict['segment_meta']['index_neg'])
            if line_idx_neg == -1:                                                       TopicAllProduced[topic_idx] = True   
        else:
            line_idx_neg = -1
        
        if line_idx_neg < line_idx_neg_check:
            line_idx_neg_check = line_idx_neg
            
    print('At most ' + str(-line_idx_neg_check-1) +'messages left to produce.')
    if line_idx_neg_check == -1:
        break
    if nMsg % 500 == 0:
        producer.flush()
        time.sleep(0.001)
    if nMsg >= 100000:
        break
    if nMsg % 2000 == 0:
        print('  '+ str(nMsg) + ' messages produced...')

producer.flush()
print(str(nMsg)+' lines produced.')
