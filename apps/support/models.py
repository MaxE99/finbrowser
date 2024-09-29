from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Contact(models.Model):
    """
    Represents a contact message submitted by a user.
    """

    contact_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    message = models.TextField(max_length=10000)
    date = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Returns a string representation of the contact message.

        Returns:
            str: A string containing the email and topic of the contact message.
        """
        return f"{self.email} - {self.topic}"
