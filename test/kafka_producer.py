from confluent_kafka import Producer
import sys
from random import randint
import random
import time
from datetime import datetime

# Kafka information
def conn_kafka_producer():
    # Catch Consumer instance Error
    def error_consumer(err):
        sys.stderr.write(f'Error: {err}')

    props = {
        'bootstrap.servers': 'localhost:9092',
        'error_cb': error_consumer,
        'max.in.flight.requests.per.connection': 1
    }
    producer = Producer(props)
    return producer

def kafka_producer_main_rs(topic, user_id, choiceLog):
    producer = conn_kafka_producer()
    producer.produce(topic, key=user_id, value=f'{choiceLog}')
    producer.poll(0)
    print(f'key = {user_id},\nvalue = {choiceLog}')
    producer.flush(10)


if __name__ == '__main__':
    with open('../data/test_hotel_name.txt', 'r', encoding='utf8')as f:
        hotel_list = f.read(-1).split('\n')
    for i in range(500):
        hotel = random.choice(hotel_list).replace(' ', '')
        timeDate = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        num1 = randint(0, 9)
        num2 = randint(0, 9)
        user_id = f'U8a6e3915313149a9d5b445862b797{num1}{num2}a'
        kafka_producer_main_rs('pro_test1', user_id, hotel)
        print(user_id, hotel)
        time.sleep(1)
        # time.sleep(random.choice(range(3)))
