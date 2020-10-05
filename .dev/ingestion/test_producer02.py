import sys

bucketName = sys.argv[1]
fileName = sys.argv[2]
bootstrapServer = sys.argv[3]
nTopic = int(sys.argv[4])

# Create topics
from kafka.admin import KafkaAdminClient, NewTopic
admin_client = KafkaAdminClient(
    bootstrap_servers=bootstrapServer,
    client_id='test'
)

topic_list = []
for t in range(nTopic):
    topic = 'ecg-'+str(t).zfill(6)
    topic_list.append(NewTopic(name=topic, num_partitions=1, replication_factor=2))
admin_client.create_topics(new_topics=topic_list, validate_only=False)
print(str(nTopic)+' topics have been created')


# read file from s3
import boto3
s3    = boto3.resource('s3')
obj   = s3.Object(bucketName,fileName)
body  = obj.get()['Body'].read().decode('utf-8')
lines = body.split('\n')
print(fileName)
# produce messages
# dd = np.array(d["signal"].strip("[]").split(","))
# produce

from kafka import KafkaProducer
import json
producer = KafkaProducer(bootstrap_servers=bootstrapServer)
print(bootstrapServer)

nLine = 0
for line in lines:
    if line == '':
        continue
    msg_dict = json.loads(line)
    Topic    = msg_dict['topic']
    ssp      = Topic.split('-')
    if int(ssp[1]) >= nTopic:
        continue
    producer.send(Topic, value=line.encode('utf-8'))
    nLine += 1
print(Topic)
print(str(nLine)+' lines produced')
