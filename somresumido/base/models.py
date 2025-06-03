from datetime import datetime

from django.db import models

from somresumido.base.managers import SoftDeletionManager


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = datetime.now()
        self.save()

    def hard_delete(self):
        super().delete()
