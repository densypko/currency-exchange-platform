from django.db import models


class TimeAuditedModel(models.Model):
    creation_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    modification_datetime = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True
