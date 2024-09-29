from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
import psycopg2
import json

# Kafka configuration for CDC
KAFKA_BROKER_URL = 'localhost:9092'
TOPIC_NAME = 'dbhistory.sqlite'

def update_postgresql(data):
    pg_conn = psycopg2.connect(
        dbname="product_catalog",
        user="postgres",
        password="password",
        host="localhost",
        port="5432"
    )
    cursor = pg_conn.cursor()

    if data['op'] == 'c':  # 'c' stands for create (insert)
        cursor.execute(
            "INSERT INTO products (name, description, price) VALUES (%s, %s, %s)",
            (data['after']['name'], data['after']['description'], data['after']['price'])
        )
    elif data['op'] == 'u':  # 'u' stands for update
        cursor.execute(
            "UPDATE products SET name=%s, description=%s, price=%s WHERE id=%s",
            (data['after']['name'], data['after']['description'], data['after']['price'], data['after']['id'])
        )
    elif data['op'] == 'd':  # 'd' stands for delete
        cursor.execute(
            "DELETE FROM products WHERE id=%s", (data['before']['id'],)
        )

    pg_conn.commit()
    cursor.close()
    pg_conn.close()

def process_cdc_message(message):
    data = json.loads(message)
    update_postgresql(data)

def cdc_sync_job():
    env = StreamExecutionEnvironment.get_execution_environment()

    kafka_consumer = FlinkKafkaConsumer(
        topics=[TOPIC_NAME],
        value_deserializer=SimpleStringSchema(),
        properties={
            'bootstrap.servers': KAFKA_BROKER_URL,
            'group.id': 'flink_cdc_consumer'
        }
    )

    kafka_stream = env.add_source(kafka_consumer)
    
    kafka_stream.map(process_cdc_message)
    
    env.execute("Flink CDC Sync Job")

if __name__ == '__main__':
    cdc_sync_job()
