# Django imports
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MaxLengthValidator


# Local imports
from apps.source.models import Source
from apps.article.models import Article
from apps.stock.models import Stock
from apps.home.managers import NotificationMessageManager, NotificationManager

User = get_user_model()


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    keyword = models.CharField(
        max_length=30,
        null=True,
        validators=[MinLengthValidator(3), MaxLengthValidator(30)],
    )
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "source"],
                name="unique_source_notification",
            ),
            models.UniqueConstraint(
                fields=["user", "keyword"],
                name="unique_keyword_notification",
            ),
            models.UniqueConstraint(
                fields=["user", "stock"],
                name="unique_stock_notification",
            ),
        ]

    objects = NotificationManager()

    def __str__(self):
        if self.stock:
            return f"{self.user} - {self.stock}"
        elif self.source:
            return f"{self.user} - {self.source}"
        else:
            return f"{self.user} - {self.keyword}"


class NotificationMessage(models.Model):
    notification_message_id = models.AutoField(primary_key=True)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    date = models.DateTimeField()
    user_has_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ("-date",)
        constraints = [
            models.UniqueConstraint(
                fields=["notification", "article"], name="unique_notification_message"
            )
        ]

    objects = NotificationMessageManager()

    def __str__(self):
        return f"{self.notification} - {self.article}"


class UserFeed(models.Model):
    feed_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    interested_sectors = models.JSONField(default=dict)
    content = models.ManyToManyField(Article, related_name="feed_content", blank=True)
    recommended_sources = models.ManyToManyField(
        Source, related_name="feed_sources", blank=True
    )
    last_content_update = models.DateTimeField()

    def __str__(self):
        return f"{self.feed_id} - {self.user}"
