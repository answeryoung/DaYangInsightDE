import sys

bucketName = sys.argv[1]
fileName = sys.argv[2]
bootstrapServer = sys.argv[3]
Topic = sys.argv[4]


# boto3 to aws S3
import boto3
s3  = boto3.resource('s3')

# fileName   = 'test.csv'
obj   = s3.Object(bucketName,fileName)
print(fileName)


# kafka
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers=bootstrapServer) 
print(bootstrapServer)
# produce
body  = obj.get()['Body'].read().decode('utf-8')
lines = body.split('\n')

nLine = 0
for line in lines:
    if line == '':
        continue
    producer.send(Topic, value=line.encode('utf-8'))
#     producer.flush()
#     print(line)
    nLine += 1
print(Topic)
print(str(nLine)+' lines produced')
