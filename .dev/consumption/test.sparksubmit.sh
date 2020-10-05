pythonDependencies = ""

spark-submit --master spark://10.0.0.10:7077 \
  --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 \
  --py-files pythonDependencies test_spark_streaming_kafka_integration.py

bin/spark-submit --jars \
  external/kafka-assembly/target/scala-*/spark-streaming-kafka-assembly-*.jar \
  examples/src/main/python/streaming/kafka_wordcount.py \
  localhost:2181 test`

spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.0.2 \
  test_spark_streaming_kafka_integration_direct.py \
  '10.0.0.7:9092,10.0.0.8:9092,10.0.0.9:9092' 'test2'
