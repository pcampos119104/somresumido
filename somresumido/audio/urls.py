from django.urls import path

from somresumido.audio.views import Create, listing

app_name = 'audio'
urlpatterns = [
    path('create/', Create.as_view(), name='create'),
    path('', listing, name='listing'),
]
