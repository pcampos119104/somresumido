import requests
from somresumido.audio.models import Audio
from celery import shared_task
from celery.signals import celeryd_after_setup
import redis
import json
from django.conf import settings


@shared_task
def process_audio_task(audio_id):
    # Enviar webhook para o n8n
    webhook_url = settings.N8N_WEBHOOK
    payload = {
        'audio_id': audio_id,
        'original_path': Audio.objects.get(id=audio_id).original_file.name
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return f"Tarefa enviada para n8n: {response.text}"
    except requests.RequestException as e:
        return f"Erro ao enviar para n8n : {str(e)}"


@shared_task
def process_redis_messages():
    print("Iniciando subscrição no Redis: canal audio_processed")
    r = redis.Redis(host='redis', port=6379, db=0)
    pubsub = r.pubsub()
    pubsub.subscribe('audio_processed')
    for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                audio_id = int(data['audio_id'])
                processed_path = data['processed_path']
                audio = Audio.objects.get(id=audio_id)
                storage = audio.processed_file.storage  # Acessa o S3Boto3Storage
                if storage.exists(processed_path):  # Verifica se o arquivo existe no MinIO
                    audio.processed_file = processed_path
                    audio.status = 'PROCESSING'
                    audio.save()
                    print(f"Áudio {audio_id} atualizado: {processed_path}")
                else:
                    print(f"Arquivo {processed_path} não encontrado no MinIO")
            except Exception as e:
                print(f"Erro ao processar mensagem: {str(e)}")

@celeryd_after_setup.connect
def setup_direct_queue(sender, instance, **kwargs):
    process_redis_messages.delay()
