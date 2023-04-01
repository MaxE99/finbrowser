# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail


# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.source.models import SourceRating, Source

User = get_user_model()


class TestSourceRatingViewSet(CreateTestInstances, APITestCase):
    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_user = get_object_or_404(User, username="TestUser2")
        new_source = get_object_or_404(Source, name="TestSource1")
        data = {"user": new_user.pk, "source": new_source.pk, "rating": 1}
        response = self.client.put("/api/source_ratings/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"rating": 1}
        response = self.client.patch("/api/source_ratings/1/", data, format="json")
        self.assertEqual(response.status_code, 405)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/source_ratings/1/")
        self.assertEqual(response.status_code, 405)

    def test_post_anon(self):
        data = {"rating": 5, "source": 1}
        response = self.client.post("/api/source_ratings/", data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="Authentication credentials were not provided.",
                code="not_authenticated",
            ),
        )

    def test_post_registered_update(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ratings_ammount = SourceRating.objects.count()
        data = {"rating": 1, "source": 1}
        response = self.client.post("/api/source_ratings/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(5, get_object_or_404(SourceRating, pk=1).rating)
        self.assertEqual(initial_ratings_ammount, SourceRating.objects.count())

    def test_post_registered_new(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ratings_ammount = SourceRating.objects.count()
        source = get_object_or_404(Source, pk=2)
        initial_average_rating = source.average_rating
        initial_rating_ammount = source.ammount_of_ratings
        data = {"rating": 1, "source": 2}
        response = self.client.post("/api/source_ratings/", data, format="json")
        self.assertEqual(response.status_code, 201)
        source.refresh_from_db()
        self.assertEqual(initial_ratings_ammount, SourceRating.objects.count() - 1)
        self.assertNotEqual(initial_average_rating, source.average_rating)
        self.assertEqual(initial_rating_ammount + 1, source.ammount_of_ratings)
