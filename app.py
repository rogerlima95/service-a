from flask import Flask, request, jsonify
import pika
import json
import os

app = Flask(__name__)

# Configurações do RabbitMQ
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = os.getenv('RABBITMQ_PORT', '5672')
rabbitmq_queue = os.getenv('RABBITMQ_QUEUE', 'queue')
rabbitmq_user = os.getenv('RABBITMQ_USER', 'user')
rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'user')

def send_to_rabbitmq(message):
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, port=int(rabbitmq_port), credentials=credentials))
    channel = connection.channel()

    # Declara a fila se ela não existir
    channel.queue_declare(queue=rabbitmq_queue, durable=True)

    # Envia a mensagem para a fila
    channel.basic_publish(
        exchange='',
        routing_key=rabbitmq_queue,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Torna a mensagem persistente
        )
    )

    # Fecha a conexão
    connection.close()

@app.route('/api/v1/strings', methods=['POST'])
def receive_strings():
    data = request.get_json()
    if not data or 'strings' not in data:
        return jsonify({'error': 'O JSON deve conter a chave "strings" com uma lista de strings.'}), 400
    
    strings = data['strings']
    if not isinstance(strings, list):
        return jsonify({'error': '"strings" deve ser uma lista.'}), 400

    # Envia as strings para o RabbitMQ
    send_to_rabbitmq(strings)

    return jsonify({'message': 'Strings recebidas e enviadas para o RabbitMQ com sucesso!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)