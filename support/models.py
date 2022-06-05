# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Local imports
from home.models import Sector

User = get_user_model()


# Create your models here.
class SourceSuggestion(models.Model):
    url = models.URLField(max_length=250, unique=True)
    sector = models.ForeignKey(Sector, null=True, on_delete=models.SET_NULL)


class FeatureSuggestion(models.Model):
    feature_suggestion_id = models.AutoField(primary_key=True)
    website_part = models.CharField(max_length=100)
    suggestion = models.CharField(max_length=200)
    explanation = models.TextField(max_length=10000)

    def __str__(self):
        return f'{self.website_part} - {self.suggestion}'


class BugReport(models.Model):
    bug_report_id = models.AutoField(primary_key=True)
    url = models.URLField()
    type = models.CharField(max_length=200)
    explanation = models.TextField(max_length=10000)

    def __str__(self):
        return f'{self.url} - {self.type}'
