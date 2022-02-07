from django.db import models
from django.conf import settings
from django.utils import timezone
import datetime
from ssi.models import User

TOKEN_EXPIRES_AFTER_SECS = settings.TOKEN_EXPIRES_AFTER_SECS
TOKEN_REFRESH_AFTER_SECS = settings.TOKEN_REFRESH_AFTER_SECS


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    token = models.CharField(max_length=255, unique=True)
    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def has_expired(self, current_time):
        """Checks expiration with respect to last_time_used"""
        expires_after = datetime.timedelta(seconds=TOKEN_EXPIRES_AFTER_SECS)
        return self.last_used_at + expires_after <= current_time

    def refresh_if_needed(self, current_time):
        """Updates last_time_used to current_time if the latter is within
        limits"""
        refresh_rate = datetime.timedelta(seconds=TOKEN_REFRESH_AFTER_SECS)
        if self.last_used_at + refresh_rate <= current_time:
            self.last_used_at = current_time
            self.save()
