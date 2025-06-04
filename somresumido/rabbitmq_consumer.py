# audio/rabbitmq_consumer.py
import json
import logging
import os
import time

import django
import pika
from botocore.exceptions import ClientError

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'somresumido.settings')
try:
    django.setup()
except Exception as e:
    logger.error(f'Erro ao configurar Django: {str(e)}')
    raise

from somresumido.audio.models import Audio  # noqa: E402
rabbitmq_user = os.environ.get('RABBITMQ_USER', 'guest')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD', 'guest')
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_port = os.environ.get('RABBITMQ_PORT', '5672')


def wait_for_rabbitmq():
    """Aguarda até que o RabbitMQ esteja disponível."""
    max_attempts = 30
    attempt = 1
    while attempt <= max_attempts:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password),
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            connection.close()
            logger.info('Conexão com RabbitMQ estabelecida com sucesso.')
            return
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f'Tentativa {attempt}/{max_attempts} falhou: {str(e)}. Aguardando 5s...')
            time.sleep(5)
            attempt += 1
    logger.error('Não foi possível conectar ao RabbitMQ após várias tentativas.')
    raise Exception('Falha ao conectar ao RabbitMQ')


def consume_rabbitmq():
    logger.info('Iniciando consumidor RabbitMQ: fila audio_processed')

    # Aguardar RabbitMQ
    wait_for_rabbitmq()

    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    credentials=pika.PlainCredentials(rabbitmq_user, rabbitmq_password),
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue='audio_processed', durable=True)

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    logger.info(f'Dados recebidos: {data}')
                    audio_id = int(data['audio_id'])
                    processed_path = data['processed_path']
                    audio = Audio.objects.get(id=audio_id)
                    storage = audio.processed_file.storage
                    logger.info(f'Storage configurado: {storage}')
                    if storage.exists(processed_path):
                        audio.processed_file = processed_path
                        audio.status = 'PROCESSING'
                        audio.save()
                        logger.info(f'Áudio {audio_id} atualizado: {processed_path}')
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        logger.warning(f'Arquivo {processed_path} não encontrado no MinIO')
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except Audio.DoesNotExist:
                    logger.error(f'Áudio {audio_id} não encontrado')
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                except ClientError as e:
                    logger.error(f'Erro S3: {e.response["Error"]["Code"]} - {e.response["Error"]["Message"]}')
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except Exception as e:
                    logger.error(f'Erro ao processar mensagem: {str(e)}')
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='audio_processed', on_message_callback=callback)
            logger.info('Aguardando mensagens na fila audio_processed...')
            channel.start_consuming()
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.AMQPChannelError) as exc:
            logger.error(f'Erro na conexão com RabbitMQ: {str(e)}. Reconectando em 10s...')
            time.sleep(10)
        except Exception as e:
            logger.error(f'Erro inesperado: {str(e)}')
            time.sleep(10)


if __name__ == '__main__':
    consume_rabbitmq()
