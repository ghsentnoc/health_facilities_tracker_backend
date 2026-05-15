import os
import sys

import pika
from pika.adapters.blocking_connection import BlockingChannel


def main() -> None:
    """Main function to consume messages from RabbitMQ."""
    # establish a connection to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))

    # create a channel
    channel = connection.channel()

    # declare a queue
    channel.queue_declare(queue="hello_world_queue", durable=True, arguments={"x-queue-type": "quorum"})

    # consume a message from the queue
    def callback(
        channel: BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.BasicProperties, body: bytes
    ) -> None:
        """Callback function to process the received message."""
        print(f" [x] Received '{body.decode()}'")

    channel.basic_consume(queue="hello_world_queue", auto_ack=True, on_message_callback=callback)
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
