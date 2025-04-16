import pika
import time
from datetime import datetime

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue_name = 'log_queue'
channel.queue_declare(queue=queue_name, durable=True)  # deklaracja opcjonalna, ale bezpieczna

while True:
    message = f"Log: {datetime.now().isoformat()}"
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=message.encode(),
                          properties=pika.BasicProperties(delivery_mode=2))
    print(f"Wysłano: {message}")
    time.sleep(2)
