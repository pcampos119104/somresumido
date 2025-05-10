from django.shortcuts import render
from django.views import View

from somresumido.audio.forms import AudioForm


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
        '''
        form = IngredientForm(request.POST)
        if not form.is_valid():
            return render(request, self.template, context={'form': form})

        form.instance.owner = request.user
        form.save()
        messages.success(request, 'Ingrediente criado.')
        return render(request, self.template, status=201)
        '''
        return render(request, self.template, context={'base_template': base_template})
