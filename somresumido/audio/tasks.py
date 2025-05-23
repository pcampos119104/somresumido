import requests
from somresumido.audio.models import Audio
from celery import shared_task
import redis
import json
import boto3
from django.conf import settings


@shared_task
def process_audio_task(audio_id):
    # Enviar webhook para o n8n
    webhook_url = 'http://n8n:5678/webhook-test/process-audio'
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
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(f"Mensagem recebida: {message}")
        print(
            f"Configurações do storage: AWS_ACCESS_KEY_ID={settings.AWS_ACCESS_KEY_ID}, AWS_S3_ENDPOINT_URL={settings.AWS_S3_ENDPOINT_URL}")
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                print(f"Dados desserializados: {data}")
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
