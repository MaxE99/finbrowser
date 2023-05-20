# Django imports
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    message = models.TextField(max_length=10000)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.topic}"
