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


@shared_task
def process_rabbitmq_messages():
    print("Iniciando consumo no RabbitMQ: fila audio_processed")
    print(f"Configurações do storage: AWS_ACCESS_KEY_ID={settings.AWS_ACCESS_KEY_ID}, AWS_S3_ENDPOINT_URL={settings.AWS_S3_ENDPOINT_URL}")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
        channel.queue_declare(queue='audio_processed', durable=True)
        def callback(ch, method, properties, body):
            try:
                data = json.loads(body)
                print(f"Dados recebidos: {data}")
                audio_id = int(data['audio_id'])
                processed_path = data['processed_path']
                audio = Audio.objects.get(id=audio_id)
                storage = audio.processed_file.storage
                print(f"Storage configurado: {storage}")
                if storage.exists(processed_path):
                    audio.processed_file = processed_path
                    audio.status = 'PROCESSING'
                    audio.save()
                    print(f"Áudio {audio_id} atualizado: {processed_path}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    print(f"Arquivo {processed_path} não encontrado no MinIO")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except Audio.DoesNotExist:
                print(f"Áudio {audio_id} não encontrado")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except ClientError as e:
                print(f"Erro S3: {e.response['Error']['Code']} - {e.response['Error']['Message']}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            except Exception as e:
                print(f"Erro ao processar mensagem: {str(e)}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        channel.basic_consume(queue='audio_processed', on_message_callback=callback)
        channel.start_consuming()
    except Exception as e:
        print(f"Erro na conexão com RabbitMQ: {str(e)}")
        raise

@celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs):
    print("Enfileirando process_rabbitmq_messages via celeryd_after_setup...")
    process_rabbitmq_messages.delay()
    print("Tarefa process_rabbitmq_messages enfileirada.")