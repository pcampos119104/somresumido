import requests
from botocore.exceptions import ClientError

from somresumido.audio.models import Audio
from celery import shared_task
from celery.signals import celeryd_after_setup
import redis
import pika
import json
from django.conf import settings


@shared_task(bind=True, max_retries=5)
def process_audio_task(self, audio_id):
    print(f"Iniciando process_audio_task para audio_id: {audio_id}")
    try:
        audio = Audio.objects.get(id=audio_id)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='new_audio', durable=True)
        message = {'audio_id': audio.id, 'original_path': audio.original_file.name}
        channel.basic_publish(
            exchange='',
            routing_key='new_audio',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        print(f"Mensagem publicada no RabbitMQ: {message}")
    except Audio.DoesNotExist:
        print(f"Áudio {audio_id} não encontrado")
        raise
    except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as exc:
        print(f"Erro ao conectar ao RabbitMQ: {exc}. Tentando novamente em 10s...")
        raise self.retry(countdown=10, exc=exc)

