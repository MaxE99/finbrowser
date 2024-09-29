from typing import Dict, Tuple, Any

from django.db import models


class NotificationManager(models.Manager):
    """
    Manager for handling notifications related to users.
    """

    def get_notification_types(self, user) -> Dict[str, models.QuerySet]:
        """
        Retrieves different types of notifications for the given user.

        Args:
            user: The user for whom to retrieve notifications.

        Returns:
            Dict[str, QuerySet]: A dictionary containing QuerySets of different notification types.
        """
        return {
            "source_notifications": self.filter(
                user=user, source__isnull=False
            ).select_related("source"),
            "stock_notifications": self.filter(
                user=user, stock__isnull=False
            ).select_related("stock"),
            "keyword_notifications": self.filter(user=user, keyword__isnull=False),
        }

    def check_stock_notification_exists(self, user, stock) -> int | bool:
        """
        Checks if a stock notification exists for the given user.

        Args:
            user: The user to check notifications for.
            stock: The stock to check for notifications.

        Returns:
            int | bool: The notification ID if it exists, otherwise False.
        """
        notification = self.filter(user=user, stock=stock)
        if notification.exists():
            return notification.first().notification_id
        return False

    def check_source_notification_exists(self, user: Any, source: Any) -> int | bool:
        """
        Checks if a source notification exists for the given user.

        Args:
            user (Any): The user to check notifications for.
            source (Any): The source to check for notifications.

        Returns:
            int | bool: The notification ID if it exists, otherwise False.
        """
        notification = self.filter(user=user, source=source)
        if notification.exists():
            return notification.first().notification_id
        return False


class NotificationMessageManager(models.Manager):
    """
    Manager for handling notification messages.
    """

    def _get_notifications(self, notifications: models.QuerySet) -> models.QuerySet:
        """
        Private method to filter and select related objects for notifications.

        Args:
            notifications (QuerySet): A QuerySet of notifications to filter.

        Returns:
            QuerySet: A QuerySet of filtered notifications with selected related objects.
        """
        return self.filter(notification__in=notifications).select_related(
            "article",
            "article__source",
            "article__source__website",
            "article__tweet_type",
        )

    def get_notification_messages(
        self, notification_types: Dict[str, models.QuerySet]
    ) -> Tuple[models.QuerySet, models.QuerySet, models.QuerySet]:
        """
        Retrieves notification messages based on the provided notification types.

        Args:
            notification_types (Dict[str, QuerySet]): A dictionary of notification types.

        Returns:
            Tuple[QuerySet, QuerySet, QuerySet]: A tuple containing QuerySets of source, stock, and keyword notifications.
        """
        return (
            self._get_notifications(notification_types["source_notifications"]),
            self._get_notifications(notification_types["stock_notifications"]),
            self._get_notifications(notification_types["keyword_notifications"]),
        )

    def get_nr_of_unseen_messages(self, notifications: models.QuerySet) -> int:
        """
        Counts the number of unseen messages for given notifications.

        Args:
            notifications (QuerySet): A QuerySet of notifications.

        Returns:
            int: The number of unseen messages.
        """
        return self.filter(notification__in=notifications, user_has_seen=False).count()
