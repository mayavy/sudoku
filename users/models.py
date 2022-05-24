from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
import uuid


class CustomUserManager(UserManager):
    def create_user(self, username, email, password, **extra_fields):
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return super().create_superuser(username, email, password, **extra_fields)


class CustomUser(AbstractUser, PermissionsMixin):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)

    first_name = None
    last_name = None
    objects = CustomUserManager()

    def __str__(self):
        return self.username
