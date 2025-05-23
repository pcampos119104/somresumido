from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from somresumido.audio.forms import AudioForm
from somresumido.audio.models import Audio
from django.http import HttpResponse
import boto3
from django.conf import settings
from .tasks import process_audio_task


# @login_required
def listing(request):
    base_template = 'base/_partial_base.html' if request.htmx else 'base/_base.html'
    qtd_per_page = 10
    template = 'audio/listing.html'
    # search_term = request.GET.get('search', '')
    # recipes = Audio.objects.filter(owner=request.user).filter(title__unaccent__icontains=search_term)
    audios = Audio.objects.all()
    paginator = Paginator(audios, qtd_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'base_template': base_template,
        'page_obj': page_obj,
        # 'search_term': search_term,
    }
    return render(request, template, context)


class Create(LoginRequiredMixin, View):
    template = 'audio/create_update.html'

    def get(self, request):
        base_template = 'base/_partial_base.html' if request.htmx else 'base/_base.html'
        audio_form = AudioForm()
        context = {
            'base_template': base_template,
            'audio_form': audio_form,
        }
        return render(request, self.template, context)

    def post(self, request):
        base_template = 'base/_partial_base.html' if request.htmx else 'base/_base.html'
        form = AudioForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'base_template': base_template,
                'audio_form': form,
            }
            return render(request, self.template, context=context, status=400)

        form.instance.owner = request.user
        audio = form.save()
        process_audio_task.delay_on_commit(audio.id)
        # messages.success(request, 'Ingrediente criado.')
        return HttpResponse('<span>Enviado</span>', status=201)


def update_processed_audio(request):
    if not request.method == 'POST':
        return HttpResponse(status=400)

    audio_id = request.POST.get('audio_id')
    processed_path = request.POST.get('processed_path')
    try:
        audio = Audio.objects.get(id=audio_id)
        # Verificar se o arquivo existe no MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=processed_path)
        audio.processed_file = processed_path
        audio.status = 'PROCESSING'
        audio.save()
        return HttpResponse('Áudio processado atualizado!')
    except s3_client.exceptions.ClientError:
        return HttpResponse('Arquivo não encontrado no MinIO', status=400)
    except Exception as e:
        return HttpResponse(f'Erro: {str(e)}', status=500)
