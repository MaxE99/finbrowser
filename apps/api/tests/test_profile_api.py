# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework.exceptions import ErrorDetail

from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.accounts.models import Profile

User = get_user_model()


class TestProfileViewSet(CreateTestInstances, APITestCase):
    def test_illegal_post(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, pk=11)
        initial_ammount_of_profiles = Profile.objects.count()
        data = {"user": user.pk}
        response = self.client.post("/api/profiles/", data, format="json")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Profile.objects.count(), initial_ammount_of_profiles)

    def test_illegal_put(self):
        self.client.login(username="TestUser1", password="testpw99")
        user = get_object_or_404(User, username="TestUser1")
        data = {"user": user.pk, "account_type": "Premium"}
        response = self.client.put("/api/profiles/3/", data, format="json")
        self.assertEqual(response.status_code, 405)
        self.assertNotEqual(get_object_or_404(Profile, profile_id=3).user, user)

    def test_illegal_destroy(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.delete("/api/profiles/1/")
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Profile.objects.filter(user__username="TestUser1").count())

    def create_test_image(self):
        file = BytesIO()
        image = Image.new("RGBA", size=(50, 50), color=(155, 0, 0))
        image.save(file, "png")
        file.name = "unique-test-name.png"
        file.seek(0)
        return SimpleUploadedFile(file.name, file.read(), content_type="image/png")

    def test_patch_change_profile_pic_anon(self):
        new_image = self.create_test_image()
        data = {"profile_pic": new_image}
        response = self.client.patch("/api/profiles/1/", data, format="multipart")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"], "Authentication credentials were not provided."
        )
        self.assertFalse(get_object_or_404(Profile, pk=1).profile_pic, new_image)

    def test_patch_change_profile_pic_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_image = self.create_test_image()
        data = {"profile_pic": new_image}
        response = self.client.patch("/api/profiles/1/", data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "unique-test-name" in str(get_object_or_404(Profile, pk=1).profile_pic)
        )

    def test_patch_delete_profile_pic_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_image = self.create_test_image()
        data = {"profile_pic": new_image}
        response = self.client.patch("/api/profiles/1/", data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "unique-test-name" in str(get_object_or_404(Profile, pk=1).profile_pic)
        )
        response = self.client.patch("/api/profiles/1/", format="multipart")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Profile, pk=1).profile_pic.name, "")

    def test_patch_change_profile_pic_of_other_user(self):
        self.client.login(username="TestUser1", password="testpw99")
        new_image = self.create_test_image()
        data = {"profile_pic": new_image}
        response = self.client.patch("/api/profiles/2/", data, format="multipart")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            ErrorDetail(
                string="You do not have permission to perform this action.",
                code="permission_denied",
            ),
        )
        self.assertFalse(
            "unique-test-name" in str(get_object_or_404(Profile, pk=2).profile_pic)
        )

    def test_illegal_patch(self):
        self.client.login(username="TestUser1", password="testpw99")
        data = {"user": 2}
        response = self.client.patch("/api/profiles/1/", data, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(get_object_or_404(Profile, pk=1).user.pk, 1)
