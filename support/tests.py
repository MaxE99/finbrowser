# Django Imports
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
# Local Imports
from support.forms import  BugReportForm, FeatureSuggestionForm, SourceSuggestionForm
from support.models import BugReport, FeatureSuggestion, SourceSuggestion
from home.models import Sector

User = get_user_model()

class BugReportFormTests(TestCase):
    def test_bug_report(self):
        form_data = {'url': 'http://test.com', 'type': 'Data', 'explanation': 'Data is not showing!'}
        form = BugReportForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(BugReport.objects.filter(url="http://test.com").exists())

    def test_empty_report(self):
        form_data = {'url': '', 'type': '', 'explanation': ''}
        form = BugReportForm(data=form_data)
        self.assertFalse(form.is_valid())


class FeatureSuggestionFormTests(TestCase):
    def test_feature_suggestion(self):
        form_data = {'website_part': 'Feed', 'suggestion': 'More personalization', 'explanation': 'Some stuff like dark mode!'}
        form = FeatureSuggestionForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(FeatureSuggestion.objects.filter(website_part="Feed").exists())

    def test_empty_suggestion(self):
        form_data = {'website_part': '', 'suggestion': '', 'explanation': ''}
        form = FeatureSuggestionForm(data=form_data)
        self.assertFalse(form.is_valid())


class SourceSuggestionFormTests(TestCase):
    def test_feature_suggestion(self):
        sector = Sector.objects.create(name="Short", slug="short")
        form_data = {'url': 'https://www.fool.com/', 'sector': sector}
        form = SourceSuggestionForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(SourceSuggestion.objects.filter(url="https://www.fool.com/").exists())

    def test_empty_suggestion(self):
        form_data = {'url': '', 'sector': ''}
        form = SourceSuggestionForm(data=form_data)
        self.assertFalse(form.is_valid())


class BugReportViewTest(TestCase):
    def test_view(self):
        response = self.client.get(reverse('support:report-bug'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'support/report_bug.html')

class FeatureSuggestionViewTest(TestCase):
    def test_view(self):
        response = self.client.get(reverse('support:suggestions'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'support/suggestions.html')

class SourceSuggestionViewTest(TestCase):
    def test_view(self):
        response = self.client.get(reverse('support:suggest-sources'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'support/suggest_sources.html')

class PrivacyPolicyViewTest(TestCase):
    def test_view(self):
        response = self.client.get(reverse('support:privacy-policy'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'support/privacy_policy.html')

class CookieStatementViewTest(TestCase):
    def test_view(self):
        response = self.client.get(reverse('support:cookie-statement'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'support/cookie_statement.html')