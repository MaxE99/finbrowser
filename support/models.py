# Django imports
from django.db import models
# Local imports
from home.models import Sector


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
