from django import forms

from somresumido.audio.models import Audio


class AudioForm(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ('original_file',)
