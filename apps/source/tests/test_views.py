# Django imports
from django.test import TestCase

# Local imports
from apps.tests.test_instances import CreateTestInstances


class TestSourceViews(CreateTestInstances, TestCase):
    def test_source_ranking_view_filter(self):
        response = self.client.get(
            "/sources?sector=TestSector1&content=Analysis&content=Commentary&paywall=No&top_sources_only=on"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "source/source_ranking.html")
        self.assertEqual(response.context["sectors"].count(), 10)
        self.assertEqual(
            response.context["search_parameters"],
            {
                "content": ["Analysis", "Commentary"],
                "paywall": ["No"],
                "sector": ["TestSector1"],
                "top_sources_only": ["on"],
            },
        )

    def test_source_ranking_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/sources")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "source/source_ranking.html")
        self.assertEqual(response.context["sectors"].count(), 10)
        self.assertEqual(response.context["search_parameters"], {})
        self.assertEqual(response.context["user_ratings"].count(), 2)

    def test_source_ranking_view_anon(self):
        response = self.client.get("/sources")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "source/source_ranking.html")
        self.assertEqual(response.context["sectors"].count(), 10)
        self.assertEqual(response.context["search_parameters"], {})

    def test_source_detail_view_registered(self):
        self.client.login(username="TestUser1", password="testpw99")
        response = self.client.get("/source/testsource1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "source/source_profile.html")
        self.assertEqual(response.context["subscribed"], True)
        self.assertEqual(response.context["user_rating"], 5)
        self.assertEqual(response.context["source_ranking"], 3)

    def test_source_detail_view_anon(self):
        response = self.client.get("/source/testsource1")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "source/source_profile.html")
        self.assertEqual(response.context["subscribed"], None)
        self.assertEqual(response.context["user_rating"], None)
        self.assertEqual(response.context["source_ranking"], 3)
