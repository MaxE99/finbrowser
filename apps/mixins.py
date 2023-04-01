# Django imports
from django.views.generic.base import ContextMixin

# Local imports
from apps.article.models import HighlightedArticle, TrendingTopicContent
from apps.list.models import List
from apps.home.models import Notification, NotificationMessage
from apps.source.models import Source


class BasicInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
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
        context["trending_topics_search"] = TrendingTopicContent.objects.all()[:5]
        return context


class NotificationMixin(ContextMixin):
    def get_context_data(self, **kwargs):
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
            unseen_notifications = (
                source_notifications
            ) = stock_notifications = keyword_notifications = None
        context["unseen_notifications"] = unseen_notifications
        context["source_notifications"] = source_notifications
        context["stock_notifications"] = stock_notifications
        context["keyword_notifications"] = keyword_notifications
        return context


class BaseMixin(BasicInfoMixin, NotificationMixin):
    """Both Mixins are required for notifications to work on every site"""
