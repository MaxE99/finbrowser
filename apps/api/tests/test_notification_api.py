# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.source.models import Source
from apps.stock.models import Stock
from apps.home.models import Notification, NotificationMessage

User = get_user_model()


class TestNotificationViewSet(CreateTestInstances, APITestCase):
    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"source": 10}
        response = self.client.patch("/api/notifications/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_put_anon(self):
        response = self.client.put("/api/notifications/", format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_put_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_unseen_notifications = NotificationMessage.objects.filter(
            notification__user=get_object_or_404(User, username="TestUser1"),
            user_has_seen=False,
        ).count()
        response = self.client.put("/api/notifications/", format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            initial_unseen_notifications,
            NotificationMessage.objects.filter(
                notification__user=get_object_or_404(User, username="TestUser1"),
                user_has_seen=False,
            ).count(),
        )

    def test_destroy_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_notifications = Notification.objects.count()
        response = self.client.delete("/api/notifications/1/", format="json")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(initial_notifications - 1, Notification.objects.count())
        self.assertFalse(Notification.objects.filter(pk=1).count())

    def test_destroy_anon(self):
        initial_notifications = Notification.objects.count()
        response = self.client.delete("/api/notifications/1/", format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )
        self.assertEqual(initial_notifications, Notification.objects.count())
        self.assertTrue(Notification.objects.filter(pk=1).count())

    def test_destroy_other_users_notification(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_notifications = Notification.objects.count()
        response = self.client.delete("/api/notifications/2/", format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertEqual(initial_notifications, Notification.objects.count())
        self.assertTrue(Notification.objects.filter(pk=1).count())

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_stock = get_object_or_404(Stock, pk=5)
        new_source = get_object_or_404(Source, pk=1)
        new_user = get_object_or_404(User, pk=3)
        data = {
            "user": new_user.pk,
            "stock": new_stock.pk,
            "source": new_source.pk,
            "keyword": "new_keyword",
        }
        response = self.client.put("/api/notifications/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(get_object_or_404(Notification, pk=1), new_user)

    def test_post_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_notifications = Notification.objects.count()
        new_source = get_object_or_404(Source, pk=10)
        data = {
            "source": new_source.pk,
        }
        response = self.client.post("/api/notifications/", data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(initial_notifications + 1, Notification.objects.count())

    def test_post_anon(self):
        initial_notifications = Notification.objects.count()
        new_source = get_object_or_404(Source, pk=10)
        data = {
            "source": new_source.pk,
        }
        response = self.client.post("/api/notifications/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )
        self.assertEqual(initial_notifications, Notification.objects.count())

    def test_post_create_notification_for_other_user(self):
        self.client.login(username="TestUser1", password="testpw99")
        notifications_user1 = Notification.objects.filter(user__pk=1).count()
        notifications_user3 = Notification.objects.filter(user__pk=3).count()
        new_source = get_object_or_404(Source, pk=10)
        data = {"source": new_source.pk, "user": 3}
        response = self.client.post("/api/notifications/", data=data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            notifications_user1 + 1, Notification.objects.filter(user__pk=1).count()
        )
        self.assertEqual(
            notifications_user3, Notification.objects.filter(user__pk=3).count()
        )
