# Django imports
from django.test import TestCase
from django.shortcuts import get_object_or_404

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.home.models import Notification, NotificationMessage
from django.contrib.auth import get_user_model
from apps.stock.models import Stock
from apps.source.models import Source

User = get_user_model()


class TestNotificationManager(CreateTestInstances, TestCase):
    def setUp(self):
        self.user1 = User.objects.create(
            username="user1", email="email1@mail.com", password="testpassword"
        )
        self.user2 = User.objects.create(
            username="user2", email="email2@mail.com", password="testpassword"
        )
        self.tesla_stock = get_object_or_404(Stock, ticker="TSLA")
        self.notification1 = Notification.objects.create(
            user=self.user1, stock=self.tesla_stock
        )
        self.test_source = get_object_or_404(Source, name="TestSource1")
        self.notification2 = Notification.objects.create(
            user=self.user2, source=self.test_source
        )
        self.notification3 = Notification.objects.create(
            user=self.user1, keyword="python"
        )

    def test_get_notification_types(self):
        types = Notification.objects.get_notification_types(self.user1)
        self.assertEqual(types["source_notifications"].count(), 0)
        self.assertEqual(types["stock_notifications"].count(), 1)
        self.assertEqual(types["keyword_notifications"].count(), 1)

    def test_check_stock_notification_exists(self):
        exists = Notification.objects.check_stock_notification_exists(
            self.user1, self.tesla_stock
        )
        self.assertEqual(exists, self.notification1.notification_id)

    def test_check_source_notification_exists(self):
        exists = Notification.objects.check_source_notification_exists(
            self.user2, self.test_source
        )
        self.assertEqual(exists, self.notification2.notification_id)
        exists = Notification.objects.check_source_notification_exists(
            self.user1, self.test_source
        )
        self.assertFalse(exists)


class TestNotificationMessageManager(CreateTestInstances, TestCase):
    def test_get_notification_messages(self):
        user = get_object_or_404(User, username="TestUser1")
        notification_types_dict = Notification.objects.get_notification_types(user)
        (
            source_notifications,
            stock_notifications,
            keyword_notifications,
        ) = NotificationMessage.objects.get_notification_messages(
            notification_types_dict
        )
        self.assertEqual(source_notifications.count(), 2)
        self.assertEqual(stock_notifications.count(), 0)
        self.assertEqual(keyword_notifications.count(), 0)

    def test_get_nr_of_unseen_messages(self):
        user = get_object_or_404(User, username="TestUser1")
        unseen_notifications = NotificationMessage.objects.get_nr_of_unseen_messages(
            Notification.objects.filter(user=user)
        )
        self.assertEqual(unseen_notifications, 2)
