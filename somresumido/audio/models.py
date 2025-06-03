from django.contrib.auth import get_user_model
from django.db import models

from somresumido.base.models import SoftDeletionModel


class Audio(SoftDeletionModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),
        ('PROCESSING', 'Processando'),
        ('COMPLETED', 'Concluído'),
        ('FAILED', 'Falhou'),
    )

    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False)
    original_file = models.FileField(upload_to='raw/')
    processed_file = models.FileField(upload_to='processed/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    title = models.CharField(max_length=50, blank=True, null=True)
    transcription = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
