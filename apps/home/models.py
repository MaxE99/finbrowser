# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator
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
    keyword = models.CharField(max_length=30, null=True, validators=[MinLengthValidator(3), MaxLengthValidator(30)])

    def __str__(self):
        if self.list:
            return f'{self.user} - {self.list}'
        elif self.source:
            return f'{self.user} - {self.source}'
        else:
            return f'{self.user} - {self.keyword}'


class NotificationMessage(models.Model):
    notification_message_id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField()
    user_has_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ('-date', )

    def __str__(self):
        return f'{self.notification} - {self.article}'