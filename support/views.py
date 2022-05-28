# Django imports
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.urls import reverse_lazy
# Local imports
from support.forms import SourceSuggestionForm, BugReportForm, FeatureSuggestionForm
class UserFeedbackMixin(FormMixin):

    def form_valid(self, form):
        new_report = form.save(commit=False)
        new_report.reporting_user = self.request.user
        new_report.save()
        messages.success(self.request, f"Thank you! You're report has been send!")
        return super().form_valid(form)

class FaqView(TemplateView):
    template_name = 'support/faq.html'

class PrivacyPolicyView(TemplateView):
    template_name = 'support/privacy_policy.html'

class CookieStatementView(TemplateView):
    template_name = 'support/cookie_statement.html'

class TermsOfServiceView(TemplateView):
    template_name = 'support/terms_of_service.html'

class SitemapView(TemplateView):
    template_name = 'support/sitemap.html'

class AboutView(TemplateView):
    template_name = 'support/about.html'

class ReportBugView(FormView, UserFeedbackMixin):
    template_name = 'support/report_bug.html'
    form_class = BugReportForm
    success_url = reverse_lazy('home:main')

class FeatureSuggestionView(FormView, UserFeedbackMixin):
    template_name = 'support/suggestions.html'
    form_class = FeatureSuggestionForm
    success_url = reverse_lazy('home:main')

class SourceSuggestionView(FormView, UserFeedbackMixin):
    template_name = 'support/suggest_sources.html'
    form_class = SourceSuggestionForm
    success_url = reverse_lazy('home:main')
