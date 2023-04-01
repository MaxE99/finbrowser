# Django imports
from django.db import models


class NotificationManager(models.Manager):
    def get_notification_types(self, user):
        return {
            "source_notifications": self.filter(
                user=user, source__isnull=False
            ).select_related("source"),
            "stock_notifications": self.filter(
                user=user, stock__isnull=False
            ).select_related("stock"),
            "keyword_notifications": self.filter(user=user, keyword__isnull=False),
        }

    def check_stock_notification_exists(self, user, stock):
        notification = self.filter(user=user, stock=stock)
        if notification.exists():
            return notification.first().notification_id
        return False

    def check_source_notification_exists(self, user, source):
        notification = self.filter(user=user, source=source)
        if notification.exists():
            return notification.first().notification_id
        return False


class NotificationMessageManager(models.Manager):
    def get_notification_messages(self, notification_types):
        source_notifications = self.filter(
            notification__in=notification_types["source_notifications"]
        ).select_related(
            "article",
            "article__source",
            "article__source__website",
            "article__tweet_type",
        )
        stock_notifications = self.filter(
            notification__in=notification_types["stock_notifications"]
        ).select_related(
            "article",
            "article__source",
            "article__source__website",
            "article__tweet_type",
        )
        keyword_notifications = self.filter(
            notification__in=notification_types["keyword_notifications"]
        ).select_related(
            "article",
            "article__source",
            "article__source__website",
            "article__tweet_type",
        )
        return source_notifications, stock_notifications, keyword_notifications

    def get_nr_of_unseen_messages(self, notifications):
        return self.filter(notification__in=notifications, user_has_seen=False).count()
