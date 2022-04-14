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
        (ALUMNUS, 'Alumnus'),
        (STUDENT, 'Student'),
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=10, null=True)

    class Meta:
        abstract = True


class Alumnus(UserProfile):
    created_by = models.ForeignKey(
        User, related_name='created_by', null=True, on_delete=models.PROTECT
    )
    extern_id = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=2048)
    last_name = models.CharField(max_length=2048)
    father_name = models.CharField(max_length=2048, null=True)
    mother_name = models.CharField(max_length=2048, null=True)
    birthyear = models.CharField(max_length=4, null=True)
    birthdate = models.CharField(max_length=64, null=True)
    afm = models.CharField(max_length=64)

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['extern_id'] = self.extern_id
        out['first_name'] = self.first_name
        out['last_name'] = self.last_name
        out['father_name'] = self.father_name
        out['mother_name'] = self.mother_name
        out['birthyear'] = self.birthyear
        out['birthdate'] = self.birthdate
        out['email'] = self.email
        out['phone'] = self.phone
        out['afm'] = self.afm
        creator = self.created_by
        if creator:
            out['created_by'] = show_user(creator)
        return out
