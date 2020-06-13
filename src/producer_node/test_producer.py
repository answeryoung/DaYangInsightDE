import sys
bootstrapServer = sys.argv[1]  #10.0.0.7:9092
fileName = sys.argv[2]
Topic = sys.argv[3]

# boto3 to aws S3
import boto3
s3  = boto3.resource('s3')
bucketName = 'dashtenn-insightde-02'
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
    print(line)
    nLine += 1
print(Topic)
print(str(nLine)+' lines produced')
