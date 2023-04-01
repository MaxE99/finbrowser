# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.list.models import List
from apps.source.models import Source
from apps.article.models import Article

User = get_user_model()


class TestListViewSet(CreateTestInstances, APITestCase):
    def test_post_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_ammount_of_lists = List.objects.count()
        response = self.client.post("/api/lists/")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(List.objects.count(), initial_ammount_of_lists + 1)

    def test_post_anon(self):
        initial_ammount_of_lists = List.objects.count()
        response = self.client.post("/api/lists/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(List.objects.count(), initial_ammount_of_lists)

    def test_patch_name_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"name": "new_name"}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(List, list_id=1).name, "new_name")

    def test_patch_name_of_other_users_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        initial_list_name = get_object_or_404(List, list_id=8).name
        data = {"name": "new_name"}
        response = self.client.patch("/api/lists/8/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertEqual(get_object_or_404(List, list_id=8).name, initial_list_name)

    def test_patch_name_anon(self):
        initial_list_name = get_object_or_404(List, list_id=1).name
        data = {"name": "new_name"}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertEqual(get_object_or_404(List, list_id=1).name, initial_list_name)

    def test_illegal_patch_list_id(self):
        self.client.login(username="TestUser1", password="testpw99")
        patched_list = get_object_or_404(List, pk=1)
        data = {"list_id": 125}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        patched_list.refresh_from_db()
        self.assertFalse(List.objects.filter(list_id=125).count())
        self.assertTrue(patched_list.pk, 1)

    def test_illegal_patch_creator(self):
        self.client.login(username="TestUser1", password="testpw99")
        patched_list = get_object_or_404(List, list_id=1)
        other_user = get_object_or_404(User, pk=2)
        data = {"creator": other_user.pk}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        patched_list.refresh_from_db()
        self.assertEqual(
            patched_list.creator, get_object_or_404(User, username="TestUser1")
        )

    def test_patch_source(self):
        self.client.login(username="TestUser1", password="testpw99")
        source = get_object_or_404(Source, source_id=7)
        data = {"source_id": source.source_id}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        patched_list = get_object_or_404(List, list_id=1)
        self.assertTrue(source in patched_list.sources.all())

    def test_patch_source_other_users_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        source = get_object_or_404(Source, source_id=7)
        data = {"source_id": source.source_id}
        response = self.client.patch("/api/lists/8/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        patched_list = get_object_or_404(List, list_id=8)
        self.assertFalse(source in patched_list.sources.all())

    def test_patch_article(self):
        self.client.login(username="TestUser1", password="testpw99")
        article = get_object_or_404(Article, article_id=7)
        data = {"article_id": article.article_id}
        response = self.client.patch("/api/lists/1/", data=data, format="json")
        self.assertEqual(response.status_code, 200)
        patched_list = get_object_or_404(List, list_id=1)
        self.assertTrue(article in patched_list.articles.all())

    def test_patch_article_other_users_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        article = get_object_or_404(Article, article_id=7)
        data = {"article_id": article.article_id}
        response = self.client.patch("/api/lists/8/", data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        patched_list = get_object_or_404(List, list_id=8)
        self.assertFalse(article in patched_list.articles.all())

    def test_destroy_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, username="TestUser1")
        main_list = get_object_or_404(List, creator=user, main=True)
        response = self.client.delete("/api/lists/1/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(List.objects.filter(list_id=1).count())
        self.assertNotEqual(main_list, get_object_or_404(List, creator=user, main=True))
        self.assertTrue(List.objects.filter(main=True, creator=user).count())

    def test_destroy_other_users_list(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/lists/8/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertTrue(List.objects.filter(list_id=8).count())

    def test_destroy_anon(self):
        response = self.client.delete("/api/lists/1/")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertTrue(List.objects.filter(list_id=1).count())

    def test_destroy_last_list(self):
        self.client.login(username="TestUser12", password="testpw99")
        user = get_object_or_404(User, username="TestUser12")
        response = self.client.delete("/api/lists/11/")
        self.assertFalse(List.objects.filter(list_id=11).count())
        last_list = get_object_or_404(List, creator=user)
        response = self.client.delete(f"/api/lists/${last_list.list_id}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, "You are not allowed to delete your last list!")
        self.assertTrue(List.objects.filter(creator=user).count())

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {
            "name": "new_name",
            "creator": 2,
            "main": True,
        }
        response = self.client.put("/api/list/1/", data, format="json")
        self.assertEqual(response.status_code, 405)
