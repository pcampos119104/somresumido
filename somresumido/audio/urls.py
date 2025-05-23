from django.urls import path

from somresumido.audio.views import Create, update_processed_audio,listing

app_name = 'audio'
urlpatterns = [
    path('create/', Create.as_view(), name='create'),
    path('', listing, name='listing'),
    path('webhook/update-processed', update_processed_audio, name='update_processed'),
]
