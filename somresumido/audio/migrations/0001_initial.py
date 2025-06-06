# Generated by Django 5.1.6 on 2025-05-09 15:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('original_file', models.FileField(upload_to='raw/')),
                ('processed_file', models.FileField(blank=True, null=True, upload_to='processed/')),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('PENDING', 'Pendente'),
                            ('PROCESSING', 'Processando'),
                            ('COMPLETED', 'Concluído'),
                            ('FAILED', 'Falhou'),
                        ],
                        default='PENDING',
                        max_length=20,
                    ),
                ),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('transcription', models.TextField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
