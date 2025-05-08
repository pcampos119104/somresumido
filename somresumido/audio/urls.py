from django.urls import path

from somresumido.audio.views import Create

app_name = 'audio'
urlpatterns = [
    path('', Create.as_view(), name='create'),
]
