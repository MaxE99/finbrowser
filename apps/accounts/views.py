# Django imports
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

# Python imports
# Local imports
from apps.accounts.forms import (
    EmailAndUsernameChangeForm,
    PasswordChangingForm,
    TimezoneChangeForm,
)
from apps.mixins import BaseMixin
from apps.home.models import Notification
from apps.logic.services import handle_settings_actions


class SettingsView(LoginRequiredMixin, TemplateView, BaseMixin):
    template_name = "accounts/settings.html"

    def post(self, request, *args, **kwargs):
        handle_settings_actions(request)
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
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
