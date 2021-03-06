import json
from threading import Thread
import pika
import requests


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    payload = json.loads(body.decode('utf-8'))
    msg = requests.post("http://127.0.0.1:5000/orders/", json=payload)
    print(msg.content)


def pull_message():
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.17.0.5'))
    channel = connection.channel()

    channel.exchange_declare(exchange='order', exchange_type='topic')

    # the empty string - create a random queue name by the broker
    # The exclusive flag - when the consumer connection is closed, the queue is deleted.
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    # * (star) can substitute for exactly one word.
    # # (hash) can substitute for zero or more words.
    channel.queue_bind(exchange='order', queue=queue_name, routing_key="order.create.*.*")

    print(' [*] Waiting for messages. To exit press CTRL+C ' + queue_name)

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)

    channel.start_consuming()


class MessagePuller(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        while True:
            pull_message()
