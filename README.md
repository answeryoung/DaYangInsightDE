# **CardioGrip** *--Pulse Diagnosis at Your Fingertips*
### **Da Yang** - Insight Fellow in Data Engineering (Silicon Valley, Summer 2020)
The overwhelming need for telemedicine has inspired this project.
To ease the pain of transmitting ECG and other biomarker data over video conferencing platform during doctor's virtual visit,
The potential to collect the data generated and reduce associated network usage can be desirable. 
I build a pipeline for aggregating, enriching, and communicating these data.

## Objective
The goal is near real-time processing and forwarding electrocardiography (ECG or EKG) data to care providers. At the same time, these data are aggregated (data aggregation can be electively disabled).

## Approach
A simulated real-time data source, based on an existing dataset that contains ECG data, is used.  The original data are continuous ECG waves that are break into small segments. These segments are packaged in the json format. Each json structure is produced as a message and sent to a Kafka cluster. A Spark cluster subscribes to the Kafka cluster and extract features from the data received. For the current project, the time locations of the P T and QRS peaks are the only features being extracted (see figure below).
![architecture]( https://i.pinimg.com/originals/2b/c4/68/2bc468ca7a012a8bb595e55607bb1a0f.jpg)
The signal segment, along with features extracted, is put in a PostgreSQL database. Near-live queries are run behind a tableau dashboard.

## Pipeline
 ![Pipeline]( .png/Architecture.png)
1.	There are 7,511 simulated patients, with their ECG data stored as 7,511 json objects in an AWS S3 Bucket. In each json object (“file”), there are many separate json structures with identical schema. Each structure contains the signal of one R-peak-to-R-peak heartbeat. The typical size of the structures is 3 kB. 
2.	Kafka-python producer programs are run on EC2 instances. Those producer programs send those structures as messages to a three-broker Kafka cluster. The data from one subject is published to one Kafka topic, and vice versa.
3.	Spark subscribe to a “pattern” of topics from the Kafka cluster and consume the data received as a direct stream. For each segment of ECG signals P, T, Q, and S are time-wise located. Then, all together, put into a database managed by PostgreSQL.
4.	A tableau dashboard is utilized to simulate the experience of the remote care provider. The patient could certainly have access to the extracted features.

## Demo
Yet to come.

## Challenges
### [x] Kafka-producer connection reliability
The Kafka would occasionally lose over half the messages sent by the producer program. I speculate the cause being this project does not use dedicated hardware. The workaround I implemented is for every 500 messages produced by a producer program, the thread sleep for 1 ms.

### [ ] Processing consecutive segments of signals
Many QRS analysis algorithms have been developed since the invention of the ECG machine over a century ago. Those algorithms are developed for signal segments with R peak in the middle. The precision resulted in this project is not ideal.

## Data Source
The data source used in this project is created based on an existing data set available from PhysioNet.org. A description of the original dataset and of preparing the data source is given in [preprocessing/ README.md]( preprocessing/ README.md).
