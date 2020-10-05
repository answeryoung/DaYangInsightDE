import sys
bootstrapServer = sys.argv[1]  #10.0.0.7:9092
out_put_file_name = sys.argv[2]
Topic = sys.argv[3]


# kafka
from kafka import KafkaConsumer
import csv
consumer = KafkaConsumer( Topic, bootstrap_servers=bootstrapServer
                        , auto_offset_reset='earliest'
                        , group_id='test_cons2'
                        , value_deserializer=lambda x: x.decode('utf-8').split(',')) 

nMsg = 0
with open(out_put_file_name,'a+', encoding= 'utf-8', newline = '') as O:
    csvWriter = csv.writer(O, delimiter=',')
    for msg in consumer:
        print("%s:%d:%d: key=%s value=%s" % (msg.topic, msg.partition,
                                             msg.offset, msg.key,
                                             msg.value))
        csvWriter.writerow(msg.value)
        nMsg += 1
        if nMsg % 2000 == 0:
            print('  '+ str(nMsg) +' messages consumed')
print('  '+ str(nMsg) +' messages consumed')




 

