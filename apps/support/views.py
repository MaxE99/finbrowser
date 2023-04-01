# Django imports
from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.urls import reverse_lazy

# Local imports
from apps.support.forms import ContactForm
from apps.home.views import BaseMixin


class UserFeedbackMixin(FormMixin):
    def form_valid(self, form):
        form.save()
        messages.success(self.request, f"Thank you! Your report has been sent!")
        return super().form_valid(form)


class PrivacyPolicyView(TemplateView, BaseMixin):
    template_name = "support/privacy_policy.html"


class CookieStatementView(TemplateView, BaseMixin):
    template_name = "support/cookie_statement.html"


class TermsOfServiceView(TemplateView, BaseMixin):
    template_name = "support/terms_of_service.html"


class ContactView(FormView, UserFeedbackMixin, BaseMixin):
    template_name = "support/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home:feed")
