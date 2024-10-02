import sys
from kafka import KafkaProducer
import json
import os
import time
from core.logger import setup_logger, log_step

# Kafka configuration
KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = 'vendor_requests'
MAX_MESSAGE_SIZE = 5 * 1024 * 1024  # 5 MB

logger = setup_logger('kafka_producer')
producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        for attempt in range(5):  # Retry up to 5 times
            try:
                log_step(logger, 1, f"Attempting to connect to Kafka broker (Attempt {attempt + 1})")
                producer = KafkaProducer(
                    bootstrap_servers=[KAFKA_BROKER_URL],
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    max_request_size=MAX_MESSAGE_SIZE,
                    buffer_memory=33554432,  # 32MB
                    batch_size=16384,
                    linger_ms=100,
                    max_block_ms=5000,
                    request_timeout_ms=30000,
                    api_version_auto_timeout_ms=5000
                )
                log_step(logger, 2, f"Successfully connected to Kafka broker on attempt {attempt + 1}")
                break
            except Exception as e:
                log_step(logger, 3, f"Failed to connect to Kafka broker on attempt {attempt + 1}. Error: {str(e)}")
                time.sleep(5)
        else:
            log_step(logger, 4, "Could not establish connection to Kafka broker after multiple attempts")
            raise Exception("Could not establish connection to Kafka broker after multiple attempts.")
    return producer

def get_size(obj, seen=None):
    """Recursively calculate size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

def send_data_to_kafka(data):
    try:
        log_step(logger, 1, f"Preparing to send data to Kafka topic: {TOPIC_NAME}")
        log_step(logger, 2, f"Data size: {get_size(data)} bytes")
        
        kafka_producer = get_kafka_producer()
        serialized_data = json.dumps(data).encode('utf-8')
        
        log_step(logger, 3, f"Serialized data size: {len(serialized_data)} bytes")
        
        if len(serialized_data) > MAX_MESSAGE_SIZE:
            log_step(logger, 4, f"WARNING: Data size ({len(serialized_data)} bytes) exceeds maximum message size ({MAX_MESSAGE_SIZE} bytes)")
            log_step(logger, 5, f"Data preview: {str(data)[:500]}...")  # Log first 500 characters of the data
            
        future = kafka_producer.send(TOPIC_NAME, value=data)
        result = future.get(timeout=60)
        log_step(logger, 6, f"Data sent to Kafka topic: {TOPIC_NAME}, partition: {result.partition}, offset: {result.offset}")
    except Exception as e:
        log_step(logger, 7, f"Failed to send data to Kafka: {str(e)}")
        log_step(logger, 8, f"Error details: {str(e)}")
        log_step(logger, 9, f"Data that failed to send: {str(data)[:1000]}...")  # Log first 1000 characters of the data
