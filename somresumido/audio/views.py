from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from somresumido.audio.forms import AudioForm
from somresumido.audio.models import Audio


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


class Create(View):
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


        # form.instance.owner = request.user
        form.instance.owner = get_user_model().objects.first()
        form.save()
        # messages.success(request, 'Ingrediente criado.')
        return HttpResponse('<span>Enviado</span>', status=201)
