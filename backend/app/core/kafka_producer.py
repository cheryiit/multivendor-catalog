from kafka import KafkaProducer
import json
import os
import time

# Kafka configuration
KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = 'vendor_requests'

producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        for attempt in range(5):  # Retry up to 5 times
            try:
                producer = KafkaProducer(
                    bootstrap_servers=[KAFKA_BROKER_URL],
                    api_version=(0, 11, 5),
                    value_serializer=lambda v: json.dumps(v).encode('utf-8')
                )
                break
            except Exception as e:
                print(f"Attempt {attempt + 1}: Failed to connect to Kafka broker. Retrying in 5 seconds...")
                time.sleep(5)
        else:
            raise Exception("Could not establish connection to Kafka broker after multiple attempts.")
    return producer

def send_data_to_kafka(data):
    try:
        kafka_producer = get_kafka_producer()
        kafka_producer.send(TOPIC_NAME, value=data)
        kafka_producer.flush()
        print(f"Data sent to Kafka topic: {TOPIC_NAME}")
    except Exception as e:
        print(f"Failed to send data to Kafka: {e}")
