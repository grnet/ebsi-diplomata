from django.db import models
from django.db.models import JSONField
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone

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

class User(AbstractBaseUser):
    STUDENT = 'student'
    ALUMNUS = 'alumnus'
    HELPDESK = 'helpdesk'
    ADMIN = 'admin'

    ROLES = [
        (STUDENT, 'Student'),
        (ALUMNUS, 'Alumnus'),
        (HELPDESK, 'Helpdesk'),
        (ADMIN, 'Admin'),
    ]

    USERNAME_FIELD = 'id'

    objects = UserManager()

    auth_provider = models.CharField(max_length=255, null=True)
    role = models.CharField(max_length=32, choices=ROLES, default=ALUMNUS)

    def __str__(self):
        return str(self.id)

    def is_student(self):
        return self.role == self.STUDENT

    def is_alumnus(self):
        return self.role == self.ALUMNUS

    def is_helpdesk(self):
        return self.role == self.HELPDESK

    def get_username(self):
        if self.is_student():
            pass
        elif self.is_alumnus():
            pass
        elif self.is_helpdesk():
            pass
        elif self._is_admin():
            pass
