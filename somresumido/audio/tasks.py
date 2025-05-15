from celery import shared_task
import requests
from somresumido.audio.models import Audio


@shared_task
def process_audio_task(audio_id):
    # Enviar webhook para o n8n
    webhook_url = 'http://n8n:5678/webhook/process-audio'
    payload = {
        'audio_id': audio_id,
        'original_path': Audio.objects.get(id=audio_id).original_file.name
    }
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        return f"Tarefa enviada para n8n: {response.text}"
    except requests.RequestException as e:
        return f"Erro ao enviar para n8n: {str(e)}"