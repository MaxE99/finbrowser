# Django imports
from django.db import models
from django.contrib.auth import get_user_model
# Local imports
from apps.list.models import List
from apps.source.models import Source
from apps.article.models import Article

User = get_user_model()

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(List, on_delete=models.CASCADE, null=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.list:
            return f'{self.user} - {self.list}'
        else:
            return f'{self.user} - {self.source}'


class NotificationMessage(models.Model):
    notification_message_id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField()
    user_has_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.notification} - {self.article}'