from typing import Any, Dict

from django.views.generic.base import ContextMixin

from apps.article.models import HighlightedArticle, TrendingTopicContent
from apps.list.models import List
from apps.home.models import Notification, NotificationMessage
from apps.source.models import Source


class BasicInfoMixin(ContextMixin):
    """
    Mixin to provide basic contextual information to the templates.

    This includes highlighted content IDs, user lists, subscribed sources,
    and trending topics based on the authenticated user.
    """

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds highlighted content, user lists, subscribed sources,
        and trending topics to the context.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Any]: The updated context with user data.
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            highlighted_content_ids = HighlightedArticle.objects.get_ids_by_user(
                self.request.user
            )
            user_lists = List.objects.filter_by_creator(self.request.user)
            subscribed_sources = Source.objects.filter_by_subscription(
                self.request.user
            )
        else:
            highlighted_content_ids = user_lists = subscribed_sources = None

        context["highlighted_content_ids"] = highlighted_content_ids
        context["user_lists"] = user_lists
        context["subscribed_sources"] = subscribed_sources
        context["trending_topics_search"] = TrendingTopicContent.objects.order_by(
            "-article__pub_date"
        )[:5]
        return context


class NotificationMixin(ContextMixin):
    """
    Mixin to provide notification-related data to the templates.

    This includes unseen notifications, source notifications,
    stock notifications, and keyword notifications for the authenticated user.
    """

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adds notification data to the context for the authenticated user.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Any]: The updated context with notification data.
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            notification_types_dict = Notification.objects.get_notification_types(
                self.request.user
            )
            (
                source_notifications,
                stock_notifications,
                keyword_notifications,
            ) = NotificationMessage.objects.get_notification_messages(
                notification_types_dict
            )
            unseen_notifications = (
                NotificationMessage.objects.get_nr_of_unseen_messages(
                    Notification.objects.filter(user=self.request.user)
                )
            )
        else:
            unseen_notifications = source_notifications = stock_notifications = (
                keyword_notifications
            ) = None

        context["unseen_notifications"] = unseen_notifications
        context["source_notifications"] = source_notifications
        context["stock_notifications"] = stock_notifications
        context["keyword_notifications"] = keyword_notifications
        return context


class BaseMixin(BasicInfoMixin, NotificationMixin):
    """Both Mixins are required for notifications to work on every site"""
