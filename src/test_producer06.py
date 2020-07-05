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

# read file from s3
import boto3
s3    = boto3.resource('s3')

from kafka import KafkaProducer
producer = KafkaProducer( bootstrap_servers=bootstrapServer
                        , acks = 1, linger_ms = 10
                        , batch_size = 786432)
print(bootstrapServer)

import time
import json

nMsg    = 0
lines   = {}
TopicOffsets            = [None] * 8000     # there will be upto 8000 topics
TopicAllProduced        = [False] * 8000
fileName_idx_min_width  = 6
fileName_idx_filler     = "0"
MessageProductionStarted= False
while True:
    line_idx_neg_check  = 0
    for topic_idx in topic_ids:
        if TopicOffsets[topic_idx] is None:
# get fileName
            fileName    = fileName_fmt.format(idx_str = str(topic_idx).zfill(6))
            s3_obj      = s3.Object(bucketName,fileName)
            print(bucketName,'/',fileName)
            obj_body    = s3_obj.get()['Body'].read().decode('utf-8')
            lines[topic_idx]        = obj_body.split('\n')
            TopicOffsets[topic_idx] = -1
        elif TopicAllProduced[topic_idx] is False:
# produce messages to each topic
            TopicOffsets[topic_idx]+= 1
            line        = lines[topic_idx][TopicOffsets[topic_idx]]
            line_dict   = json.loads(line)
            Topic       = line_dict['topic']
            producer.send(Topic, value=line.encode('utf-8'))
            nMsg        += 1
            MessageProductionStarted    = True
            line_idx        = int(line_dict['segment_meta']['index'])
            line_idx_neg    = int(line_dict['segment_meta']['index_neg'])
            if line_idx_neg == -1:
                TopicAllProduced[topic_idx] = True
            if nMsg % 500 == 0:
                # producer.flush()
                time.sleep(0.001)
            if line_idx_neg < line_idx_neg_check:
                line_idx_neg_check = line_idx_neg
        else:
            continue
        
    if MessageProductionStarted:
        print('At most ' + str(-line_idx_neg_check-1) +' messages per topic left to produce.')
        # if line_idx == 19:
        #     break
        if line_idx_neg_check == -1:
            break
    
producer.flush()
print(str(nMsg)+' lines produced.')
