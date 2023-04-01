# Django imports
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Contact(models.Model):
    contact_id = models.AutoField(primary_key=True)
    contact_email = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    explanation = models.TextField(max_length=10000)

    def __str__(self):
        return f"{self.contact_email} - {self.topic}"
