import pika

def callback(ch, method, properties, body):
    print(f"Odebrano: {body.decode()}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

queue_name = 'log_queue'
channel.queue_declare(queue=queue_name, durable=True)

channel.basic_consume(queue=queue_name, on_message_callback=callback)

print('Oczekiwanie na wiadomości...')
channel.start_consuming()
