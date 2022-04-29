from django.db import models
from django.db.models import JSONField
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.utils import timezone
import datetime


TOKEN_EXPIRES_AFTER_SECS = settings.TOKEN_EXPIRES_AFTER_SECS
TOKEN_REFRESH_AFTER_SECS = settings.TOKEN_REFRESH_AFTER_SECS


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

    def serialize(self):
        out = {}
        out['user_id'] = self.user.id
        out['value'] = self.token
        out['session_id'] = self.session_id
        out['created_at'] = self.created_at
        out['last_used_at'] = self.last_used_at
        out['is_active'] = self.is_active
        return out


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
    # TODO: Include DID field

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


class Credential(models.Model):
    """Verifiable credential"""
    holder = models.ForeignKey(Alumnus, on_delete=models.PROTECT)
    body = JSONField(null=False)

    def serialize(self):
        out = {}
        out['holder'] = self.holder.serialize()  # TODO: Should use DID
        out['body'] = self.body
        return out
