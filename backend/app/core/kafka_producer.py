from kafka import KafkaProducer
import json
import os
import time
import logging

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
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    max_request_size=1048576,  # 1MB
                    buffer_memory=33554432,  # 32MB
                    max_block_ms=5000,
                    request_timeout_ms=30000,
                    api_version_auto_timeout_ms=5000
                )
                logging.info(f"Successfully connected to Kafka broker on attempt {attempt + 1}")
                break
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1}: Failed to connect to Kafka broker. Retrying in 5 seconds...")
                logging.exception(e)
                time.sleep(5)
        else:
            raise Exception("Could not establish connection to Kafka broker after multiple attempts.")
    return producer

def send_data_to_kafka(data):
    try:
        kafka_producer = get_kafka_producer()
        future = kafka_producer.send(TOPIC_NAME, value=data)
        result = future.get(timeout=10)
        logging.info(f"Data sent to Kafka topic: {TOPIC_NAME}, partition: {result.partition}, offset: {result.offset}")
    except Exception as e:
        logging.error(f"Failed to send data to Kafka: {e}")
        logging.exception(e)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')