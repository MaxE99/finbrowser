from io import BytesIO
import os
import sys
from typing import Any, Optional

from PIL import Image
import pytz

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.postgres.fields import CICharField
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    """
    Custom user manager where the 'get' method is overridden to always
    load the related profile with the user. It also handles the creation
    of regular users, staff users, and superusers.
    """

    def get(self, *args: Any, **kwargs: Any) -> AbstractBaseUser:
        """
        Overridden method to always load the related profile when
        fetching a user.

        Args:
            *args: Positional arguments for the get method.
            **kwargs: Keyword arguments for the get method.

        Returns:
            AbstractBaseUser: A user instance with a related profile.
        """
        return super().select_related("profile").get(*args, **kwargs)

    def create_user(
        self, username: str, email: str, password: Optional[str] = None
    ) -> AbstractBaseUser:
        """
        Creates and saves a User with the given username, email, and password.

        Args:
            username (str): The username for the new user.
            email (str): The email address for the new user.
            password (str, optional): The user's password.

        Raises:
            ValueError: If the username or email is not provided.

        Returns:
            AbstractBaseUser: The created user instance.
        """
        if not username:
            raise ValueError("The username is required.")
        if not email:
            raise ValueError("The email address is required.")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(
        self, username: str, email: str, password: str
    ) -> AbstractBaseUser:
        """
        Creates and saves a staff user with the given username, email, and password.

        Args:
            username (str): The username for the staff user.
            email (str): The email address for the staff user.
            password (str): The password for the staff user.

        Returns:
            AbstractBaseUser: The created staff user instance.
        """
        user = self.create_user(username, email, password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username: str, email: str, password: str
    ) -> AbstractBaseUser:
        """
        Creates and saves a superuser with the given username, email, and password.

        Args:
            username (str): The username for the superuser.
            email (str): The email address for the superuser.
            password (str): The password for the superuser.

        Returns:
            AbstractBaseUser: The created superuser instance.
        """
        user = self.create_user(username, email, password)
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    Custom User model that uses email as the primary identifier and has additional
    fields for username, active status, staff, and admin roles.
    """

    username = CICharField(
        max_length=30,
        unique=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(30)],
    )
    email = models.EmailField(
        max_length=50,
        unique=True,
        validators=[MinLengthValidator(5), MaxLengthValidator(50)],
    )
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser

    # notice the absence of a "Password field", that is built in.

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # Email & Password are required by default.

    objects = UserManager()

    def get_full_name(self) -> str:
        """
        Retrieves the user's full name.

        Returns:
            str: The user's email, used as their full name identifier.
        """
        return self.email

    def get_short_name(self) -> str:
        """
        Retrieves the user's short name.

        Returns:
            str: The user's email, used as their short name identifier.
        """
        return self.email

    def __str__(self) -> str:
        """
        Returns the string representation of the user, which is their email.

        Returns:
            str: The user's email address.
        """
        return self.email

    def has_perm(self, perm: str, obj: Optional[models.Model] = None) -> bool:
        """
        Checks if the user has a specific permission.

        Args:
            perm (str): The permission to check.
            obj (Optional[models.Model]): The object to check the permission against.

        Returns:
            bool: True, indicating the user has the permission.
        """
        return True

    def has_module_perms(self, app_label: str) -> bool:
        """
        Checks if the user has permissions to view the app with the given label.

        Args:
            app_label (str): The label of the app.

        Returns:
            bool: True, indicating the user has permission for the app.
        """
        return True

    @property
    def is_staff(self) -> bool:
        """
        Checks if the user is a member of staff.

        Returns:
            bool: True if the user is a staff member, False otherwise.
        """
        return self.staff

    @property
    def is_admin(self) -> bool:
        """
        Checks if the user is an admin (superuser).

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.admin


User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_and_mains(
    sender: type[User], instance: User, created: bool, **kwargs: Any
):
    """
    Signal handler that creates a Profile, a main Portfolio, and a main List when a new User is created.

    Args:
        sender (type[User]): The model class that sent the signal (User).
        instance (User): The instance of the created User.
        created (bool): A boolean indicating whether a new User instance was created.
        **kwargs (Any): Additional keyword arguments passed by the signal.
    """
    if created:
        from apps.list.models import List
        from apps.stock.models import Portfolio

        Profile.objects.create(user=instance)
        Portfolio.objects.create(user=instance, name="Main Portfolio", main=True)
        List.objects.create(creator=instance, name="Main List", main=True)


def create_profile_pic_name(self, filename: str) -> str:
    """
    Generate the file path for a user's profile picture.

    The function creates a path based on the user's username and the original filename.

    Args:
        filename (str): The original filename of the profile picture.

    Returns:
        str: The generated file path for the profile picture.
    """
    path = "profile_pics/"
    format = f"{self.user.username} - {filename}"
    return os.path.join(path, format)


class Profile(models.Model):
    """
    Model representing a user's profile, linked to the User model.
    """

    ACCOUNT_TYPES = [
        ("Standard", "Standard"),
        ("Premium", "Premium"),
        ("Admin", "Admin"),
    ]
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    profile_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    profile_pic = models.ImageField(
        null=True, blank=True, upload_to=create_profile_pic_name
    )
    account_type = models.CharField(
        max_length=50, choices=ACCOUNT_TYPES, default="Standard"
    )
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default="UTC")

    def __init__(self, *args: Any, **kwargs: Any):
        """
        Initializes the Profile instance and stores the original profile picture.

        Args:
            *args (Any): Positional arguments for the model.
            **kwargs (Any): Keyword arguments for the model.
        """
        super().__init__(*args, **kwargs)
        self.__original_profile_pic = self.profile_pic

    def save(self, *args: Any, **kwargs: Any):
        """
        Saves the Profile instance. If the profile picture has changed, it resizes
        and converts it to a WEBP format before saving.

        Args:
            *args (Any): Positional arguments for the save method.
            **kwargs (Any): Keyword arguments for the save method.
        """

        if self.__original_profile_pic != self.profile_pic:
            im = Image.open(self.profile_pic)
            output = BytesIO()
            im = im.resize((175, 175))
            im.save(output, format="WEBP", quality=99)
            output.seek(0)
            self.profile_pic = InMemoryUploadedFile(
                output,
                "ImageField",
                "%s.webp" % self.profile_pic.name.split(".")[0],
                "image/webp",
                sys.getsizeof(output),
                None,
            )
        super(Profile, self).save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Returns the string representation of the Profile instance, which is the associated user's email.

        Returns:
            str: The email of the associated user.
        """
        return str(self.user)


class Website(models.Model):
    """
    Model representing a website associated with a user.
    """

    website_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, unique=True)
    url = models.URLField(blank=True)
    favicon = models.CharField(max_length=500, blank=True)
    logo = models.CharField(max_length=500, blank=True)

    def __str__(self) -> str:
        """
        Returns the string representation of the Website instance, which is the website's name.

        Returns:
            str: The name of the website.
        """
        return self.name
