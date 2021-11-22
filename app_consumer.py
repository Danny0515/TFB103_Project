# basic on python 3.6.13
from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import os
from datetime import datetime, timedelta
from hdfs import *

# Information for consumer
records_pulled = False
saveFileTime = '00:00:00'
topic = 'pro_test1'

# Information for hadoop
client = Client("http://master:50070")


def error_cb(err):
    sys.stderr.write(f'Error: {err}')

# Convert msg_key or msg_value to utf-8
def try_decode_utf8(data):
    return data.decode('utf-8') if data else None

# When commit, call this
def print_commit_result(err, partitions):
    if err:
        print(f'Failed to commit offsets: {err}: {partitions}')
    else:
        for p in partitions:
            print(f'Committed offsets for: {p.topic}-{p.partition} [offset={p.offset}]')

# Create a directory to save image
def kafka_consumer_mkdir():
    if not os.path.exists('./kafka_consumer_data'):
        os.mkdir('./kafka_consumer_data')
    elif not os.path.exists('./kafka_consumer_data'):
        os.mkdir('./kafka_consumer_data')

def conn_kafka_consumer(ip='localhost:9092'):
    props = {
        'bootstrap.servers': ip,
        'group.id': 'tfb103_g1',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False,
        # 'on_commit': print_commit_result,
        'error_cb': error_cb
    }
    consumer = Consumer(props)
    return consumer

def kafka_consumer_main_rs(consumer, topic):
    consumer.subscribe([topic])
    global records_pulled
    global saveFileTime
    try:
        while True:
            records = consumer.consume(num_messages=500, timeout=1.0)
            if not records:
                continue
            for record in records:
                if not record:
                    continue
                if record.error() and record.error().code() != KafkaError._PARTITION_EOF:
                    raise KafkaException(record.error())
                else:
                    records_pulled = True
                    # Get information
                    topicName = record.topic()
                    partition = record.partition()
                    offset = record.offset()
                    nowTime = datetime.now().strftime('%H:%M:%S')
                    todayDate = datetime.now().strftime('%Y-%m-%d')
                    year = datetime.now().year
                    lastWeek = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

                    # Get msg_key and msg_value
                    msg_key = try_decode_utf8(record.key())
                    msg_value = try_decode_utf8(record.value())
                    print(f'{topicName}-{partition}-{offset}:\n'
                          f'({msg_key}, {msg_value}, {nowTime})')

                    # Create a new file when 00:00:01 everyday
                    if nowTime == saveFileTime:
                        print('=================')
                        with open(f'data/user_mainRS_log/{year}/mainRS_log_{todayDate}.csv',
                                  'w', encoding='utf-8')as f:
                            f.write(f'{msg_key},{msg_value},{nowTime}\n')
                        # Put last week file to HDFS
                        client.upload(f'/project/tfb1031/user_mainRS_log/{year}',
                                      f'data/user_mainRS_log/{year}/mainRS_log_{lastWeek}.csv')
                        # Remove last week file after putting it on HDFS
                        os.remove(f'data/user_mainRS_log/{year}/mainRS_log_{lastWeek}.csv')
                        continue
                    else:
                        print(nowTime)
                        with open(f'./data/user_mainRS_log/{year}/mainRS_log_{todayDate}.csv',
                                  'a', encoding='utf-8')as f:
                            f.write(f'{msg_key},{msg_value},{nowTime}\n')
            # Async commit
            if records_pulled:
                consumer.commit()
    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        sys.stderr.write(str(e))
    finally:
        consumer.commit()
        consumer.close()


if __name__ == '__main__':
    consumer = conn_kafka_consumer()
    kafka_consumer_mkdir()
    print('...\n...\n...\n====== Kafka consumer start ======')
    kafka_consumer_main_rs(consumer, topic)


