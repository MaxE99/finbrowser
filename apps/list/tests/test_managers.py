# Django imports
from django.test import TestCase
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


# Local imports
from apps.tests.test_instances import CreateTestInstances
from apps.list.models import List

User = get_user_model()


class TestListManager(CreateTestInstances, TestCase):
    def test_filter_by_creator(self):
        user = get_object_or_404(User, username="TestUser1")
        user_lists = List.objects.filter_by_creator(user)
        self.assertEqual(user_lists.count(), 8)

    def test_get_highlighted_content(self):
        list = get_object_or_404(List, name="List1")
        highlighted_content = List.objects.get_highlighted_content(list)
        self.assertEqual(highlighted_content.count(), 1)
