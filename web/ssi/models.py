from django.db import models
from django.db import models
from django.db.models import JSONField

class Did(models.Model):
    """DID (body not NULL indicates resolved DID)"""
    alias = models.CharField(max_length=256, primary_key=True)
    body = JSONField(null=True)

class Credential(models.Model):
    """Verifiable credential"""
    alias = models.CharField(max_length=256, primary_key=True)
    holder = models.ForeignKey(Did, on_delete=models.DO_NOTHING)
    body = JSONField(null=False)

class Presentation(models.Model):
    """Verifiable presentation"""
    alias = models.CharField(max_length=256)
    holder = models.ForeignKey(Did, on_delete=models.DO_NOTHING)
    body = JSONField(null=False)
