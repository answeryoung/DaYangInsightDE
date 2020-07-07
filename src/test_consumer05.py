import sys
bootstrapServer = sys.argv[1]  #10.0.0.7:9092
out_put_file_name = sys.argv[2]
Topic = sys.argv[3]


# kafka
# https://towardsdatascience.com/kafka-python-explained-in-10-lines-of-code-800e3e07dad1
from kafka import KafkaConsumer
from json import loads
# from pymongo import MongoClient
import numpy as np
consumer = KafkaConsumer( Topic, bootstrap_servers=bootstrapServer
                        , auto_offset_reset='earliest'
#                         , group_id='test_cons'
                        , enable_auto_commit=False
, value_deserializer=lambda x: loads(x.decode('utf-8'))) 


# client     = MongoClient('localhost:27017')
# collection = client.test03.test03

nMsg = 0 
for msg in consumer:
    message = msg.value
    i = message['segment_meta']['index']
    i_neg = message['segment_meta']['index_neg']  
    s = message['signal']
    a = np.array(s.strip("[]").split(' '))
    print(message['topic'] + ' : part: ' + str(msg.partition)
            + ', offset: ' + str(msg.offset) 
            + ', idx: [' + str(i) + ', ' + str(i_neg),']'
            + ', len: ' + str(a.size))
            
    
#    print(len(a),len(s))
#    collection.insert_one(message)
#    print('{} added to {}'.format(message, collection))

    nMsg += 1
    if nMsg % 1000 == 0:
        print('===========================================')
#    if nMsg % 1000 == 0:
#        print('  '+ str(nMsg) +' messages consumed...')
#print('  '+ str(nMsg) +' messages consumed.')

# database_names = client.list_database_names()
# print ("databases: ", database_names)




 

