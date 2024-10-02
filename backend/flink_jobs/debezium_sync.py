from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import psycopg2
import json
import os
from backend.app.core.logger import setup_logger, log_step

logger = setup_logger('debezium_sync')

# Kafka configuration for CDC
KAFKA_BROKER_URL = os.getenv('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = 'dbhistory.sqlite'

def update_postgresql(data):
    log_step(logger, 1, f"Updating PostgreSQL with operation: {data['op']}")
    pg_conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "product_catalog"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    cursor = pg_conn.cursor()

    try:
        if data['op'] == 'c':  # 'c' stands for create (insert)
            log_step(logger, 2, "Inserting new record into PostgreSQL")
            cursor.execute(
                "INSERT INTO products (name, description, price) VALUES (%s, %s, %s)",
                (data['after']['name'], data['after']['description'], data['after']['price'])
            )
        elif data['op'] == 'u':  # 'u' stands for update
            log_step(logger, 2, f"Updating record in PostgreSQL with id: {data['after']['id']}")
            cursor.execute(
                "UPDATE products SET name=%s, description=%s, price=%s WHERE id=%s",
                (data['after']['name'], data['after']['description'], data['after']['price'], data['after']['id'])
            )
        elif data['op'] == 'd':  # 'd' stands for delete
            log_step(logger, 2, f"Deleting record from PostgreSQL with id: {data['before']['id']}")
            cursor.execute(
                "DELETE FROM products WHERE id=%s", (data['before']['id'],)
            )

        pg_conn.commit()
        log_step(logger, 3, "PostgreSQL operation completed successfully")
    except Exception as e:
        log_step(logger, 3, f"Error updating PostgreSQL: {str(e)}")
        pg_conn.rollback()
    finally:
        cursor.close()
        pg_conn.close()
        log_step(logger, 4, "PostgreSQL connection closed")

def process_cdc_message(message):
    log_step(logger, 5, "Processing CDC message")
    try:
        data = json.loads(message)
        log_step(logger, 6, f"Parsed CDC message: {data}")
        update_postgresql(data)
        log_step(logger, 7, "CDC message processed successfully")
    except json.JSONDecodeError as e:
        log_step(logger, 7, f"Error decoding CDC message: {str(e)}")
    except Exception as e:
        log_step(logger, 7, f"Error processing CDC message: {str(e)}")

def cdc_sync_job():
    log_step(logger, 8, "Starting CDC sync job")
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_consumer = FlinkKafkaConsumer(
        topics=[TOPIC_NAME],
        value_deserializer=SimpleStringSchema(),
        properties={
            'bootstrap.servers': KAFKA_BROKER_URL,
            'group.id': 'flink_cdc_consumer'
        }
    )

    log_step(logger, 9, f"Created Kafka consumer for topic: {TOPIC_NAME}")

    kafka_stream = env.add_source(kafka_consumer)
    
    kafka_stream.map(process_cdc_message)
    
    log_step(logger, 10, "Executing Flink CDC Sync Job")
    env.execute("Flink CDC Sync Job")

if __name__ == '__main__':
    cdc_sync_job()
