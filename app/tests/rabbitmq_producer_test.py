import pika

# establish a connection to RabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost", port=5672))

# create a channel
channel = connection.channel()

# declare a queue
channel.queue_declare(queue="hello_world_queue", durable=True, arguments={"x-queue-type": "quorum"})

# publish a message to the queue
channel.basic_publish(exchange="", routing_key="hello_world_queue", body="Hello, World!")
print(" [x] Sent 'Hello, World!'")

connection.close()
