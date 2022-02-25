from django.db import models
from django.contrib.auth.models import (
                                        AbstractBaseUser, PermissionsMixin,
                                        UserManager)
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


class CustomUserManager(UserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('You must provide an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        """Creates and saves a new superuser"""
        if not email:
            raise ValueError('You must provide an email address')
        superuser = self.create_user(email, password)
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save(using=self._db)
        return superuser


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Custom User model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'


class Tag(models.Model):
    """Tag model for creating recipe tags"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
