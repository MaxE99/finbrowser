from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpRequest
from django.views.generic import TemplateView

from apps.accounts.forms import (
    EmailAndUsernameChangeForm,
    PasswordChangingForm,
    TimezoneChangeForm,
)
from apps.home.models import Notification
from apps.mixins import BaseMixin


class SettingsView(LoginRequiredMixin, TemplateView, BaseMixin):
    """
    View for managing user settings. Requires user to be logged in.
    """

    template_name = "accounts/settings.html"

    def post(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> HttpResponseRedirect:
        """
        Handles POST requests for settings actions.

        Args:
            request (HttpRequest): The HTTP request object.
            *args (Any): Positional arguments passed to the method.
            **kwargs (Any): Keyword arguments passed to the method.

        Returns:
            HttpResponseRedirect: A redirect response to the current page.
        """

        if "changeProfileForm" in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(
                request.POST,
                username=request.user.username,
                email=request.user.email,
                instance=request.user,
            )
            change_timezone_form = TimezoneChangeForm(
                request.POST, instance=request.user.profile
            )

            if change_timezone_form.is_valid():
                change_timezone_form.save()
                request.session["django_timezone"] = request.POST["timezone"]
            if email_and_name_change_form.is_valid():
                request.user.save()
                request.user.profile.save()
                messages.success(request, "Profile has been updated!")
            else:
                messages.error(request, "Error: Username or email already exists!")

        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(
                user=request.user, data=request.POST or None
            )
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
                messages.success(request, "Password has been changed!")
            else:
                messages.error(request, "New password is invalid!")

        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Gets the context data for the settings view, including user notifications
        and forms for updating email, password, and timezone.

        Args:
            **kwargs (Any): Additional context parameters.

        Returns:
            Dict[str, Any]: The context data to be rendered in the template.
        """
        context = super().get_context_data(**kwargs)
        notification_types_dict = Notification.objects.get_notification_types(
            self.request.user
        )
        context["user_source_notifications"] = notification_types_dict[
            "source_notifications"
        ].order_by("source__name")
        context["user_stock_notifications"] = notification_types_dict[
            "stock_notifications"
        ].order_by("stock__ticker")
        context["user_keyword_notifications"] = notification_types_dict[
            "keyword_notifications"
        ].order_by("keyword")
        context["email_and_name_change_form"] = EmailAndUsernameChangeForm(
            username=self.request.user.username, email=self.request.user.email
        )
        context["change_password_form"] = PasswordChangingForm(self.request.user)
        context["change_timezone_form"] = TimezoneChangeForm(
            timezone=self.request.user.profile.timezone
        )
        return context
