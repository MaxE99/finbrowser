# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Local imports
from home.models import Sector

User = get_user_model()


# Create your models here.
class SourceSuggestion(models.Model):
    STATUS_CHOICES = [('Under Review', 'Under Review'),
                      ('Accepted', 'Accepted'), ('Declined', 'Declined')]
    DECLINED_REASONS = [('Not enough depth', 'Not enough depth'),
                        ('Not investment related', 'Not investment related')]
    url = models.URLField(max_length=250, unique=True)
    suggestion_date = models.DateTimeField(auto_now=True)
    sector = models.ForeignKey(Sector, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=50,
                              choices=STATUS_CHOICES,
                              default='Under Review')
    reason_for_decline = models.CharField(max_length=250,
                                          blank=True,
                                          choices=DECLINED_REASONS)

    def __str__(self):
        return f'{self.url} - {self.status}'


class FeatureSuggestion(models.Model):
    feature_suggestion_id = models.AutoField(primary_key=True)
    reporting_user = models.ForeignKey(User,
                                       null=True,
                                       on_delete=models.SET_NULL)
    website_part = models.CharField(max_length=100)
    suggestion = models.CharField(max_length=200)
    explanation = models.TextField(max_length=10000)

    def __str__(self):
        return f'{self.website_part} - {self.suggestion}'


class BugReport(models.Model):
    bug_report_id = models.AutoField(primary_key=True)
    reporting_user = models.ForeignKey(User,
                                       null=True,
                                       on_delete=models.SET_NULL)
    url = models.URLField()
    type = models.CharField(max_length=200)
    explanation = models.TextField(max_length=10000)

    def __str__(self):
        return f'{self.url} - {self.type}'
