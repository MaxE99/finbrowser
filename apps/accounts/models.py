# Django imports
from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser)
from django.contrib.postgres.fields import CICharField
from django.contrib.auth import get_user_model
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxLengthValidator
from django.core.files.uploadedfile import InMemoryUploadedFile
# Python imports
import os
from io import BytesIO
import sys
from PIL import Image
# Local imports
from apps.accounts.validators import validate_domain_available


class UserManager(BaseUserManager):
    # overwritten get so to always load profile with user
    def get(self, *args, **kwargs):
        return super().select_related('profile').get(*args, **kwargs)

    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('Users must have a username')

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, username, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(username, email, password=password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(username, email, password=password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = CICharField(max_length=30, unique=True, validators=[MaxLengthValidator(30), validate_domain_available])
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser

    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Email & Password are required by default.

    objects = UserManager()

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin


User = get_user_model()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(user=user)
        PrivacySettings.objects.create(profile=profile)


def create_profile_pic_name(self, filename):
    path = "profile_pics/"
    format = f"{self.user.username} - {filename}"
    return os.path.join(path, format)

class Profile(models.Model):
    ACCOUNT_TYPES = [('Standard', 'Standard'), ('Premium', 'Premium'), ('Admin', 'Admin')]
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    slug = models.SlugField(unique=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to=create_profile_pic_name)
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPES, default="Standard")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_profile_pic = self.profile_pic

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        if self.__original_profile_pic != self.profile_pic:
            im = Image.open(self.profile_pic)
            output = BytesIO()
            im = im.resize((175, 175))
            im.save(output, format='WEBP', quality=99)
            output.seek(0)
            self.profile_pic = InMemoryUploadedFile(output, 'ImageField', "%s.webp" % self.profile_pic.name.split('.')[0], 'image/webp', sys.getsizeof(output), None)
        super(Profile, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'slug': self.slug})

    def __str__(self):
        return str(self.user)


class Website(models.Model):
    website_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, unique=True)
    url = models.URLField(blank=True)
    favicon = models.CharField(max_length=500, blank=True)
    logo = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class PrivacySettings(models.Model):
    privacy_settings_id = models.AutoField(primary_key=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    list_subscribtions_public = models.BooleanField(default=True)
    subscribed_sources_public = models.BooleanField(default=True)
    highlighted_articles_public = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.profile} - Privacy Settings'