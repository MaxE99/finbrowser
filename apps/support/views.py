from django.contrib import messages
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.urls import reverse_lazy

from apps.support.forms import ContactForm
from apps.home.views import BaseMixin


class UserFeedbackMixin(FormMixin):
    """
    Mixin to handle user feedback forms.

    This mixin saves the form data and displays a success message upon
    successful form submission.
    """

    def form_valid(self, form: FormMixin):
        """
        Handles the valid form submission.

        Saves the form and displays a success message.

        Args:
            form (FormMixin): The form that has been validated.

        Returns:
            HttpResponse: A response to redirect to the success URL.
        """
        form.save()
        messages.success(self.request, f"Thank you! Your report has been sent!")
        return super().form_valid(form)


class PrivacyPolicyView(TemplateView, BaseMixin):
    """
    View to display the privacy policy page.

    Inherits from TemplateView and BaseMixin to include
    common context data.
    """

    template_name = "support/privacy_policy.html"


class CookieStatementView(TemplateView, BaseMixin):
    """
    View to display the cookie statement page.

    Inherits from TemplateView and BaseMixin to include
    common context data.
    """

    template_name = "support/cookie_statement.html"


class TermsOfServiceView(TemplateView, BaseMixin):
    """
    View to display the terms of service page.

    Inherits from TemplateView and BaseMixin to include
    common context data.
    """

    template_name = "support/terms_of_service.html"


class ContactView(FormView, UserFeedbackMixin, BaseMixin):
    """
    View to handle user contact requests.

    Inherits from FormView and UserFeedbackMixin to manage the
    contact form submission and user feedback.
    """

    template_name = "support/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home:feed")
