# Django imports
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseRedirect
# Local imports
from apps.accounts.forms import EmailAndUsernameChangeForm, PasswordChangingForm, ProfileChangeForm, PrivacySettingsForm
from apps.mixins import BaseMixin, BaseFormMixins
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.models import Website
from apps.source.models import Source
from apps.home.models import Notification


class SettingsView(LoginRequiredMixin, TemplateView, BaseMixin):
    template_name = 'accounts/settings.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST or 'createKeywordNotificationForm' in request.POST:
            post_res = BaseFormMixins.post(self, request, multi_form_page=True)
            if post_res == 'Failed' or post_res == 'Notification created':
                return HttpResponseRedirect(self.request.path_info)
            profile_slug, list_slug = post_res
            return redirect('list:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'changeProfileForm' in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(request.POST, username=request.user.username, email=request.user.email, instance=request.user)
            profile_change_form = ProfileChangeForm(request.POST, request.FILES, instance=request.user.profile)
            if profile_change_form.is_valid():
                profile_change_form.save()
                if email_and_name_change_form.is_valid():
                    request.user.save()
                    request.user.profile.save()
                    messages.success(request, 'Username and Email have been updated!')
                else:
                    messages.error(request, "Error: Username or email already exists!")
            else:
                messages.error(request, "Error: Currently only PNG and JPG files are supported!")
        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(user=request.user, data=request.POST or None)
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
                messages.success(request, 'Password has been changed!')
            else:
                messages.error(request, 'New password is invalid!')
        elif 'changePrivacySettingsForm' in request.POST:
            privacy_settings_form = PrivacySettingsForm(request.POST, instance=request.user.profile.privacysettings)
            if privacy_settings_form.is_valid():
                form = privacy_settings_form.save(commit=False)
                form.profile = request.user.profile
                form.save()
                messages.success(request, 'Privacy settings have been updated!')
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribed_sources'] = Source.objects.filter_by_subscription(self.request.user)
        context['websites'] = Website.objects.exclude(name="News")
        context['notifications'] = Notification.objects.filter(user=self.request.user).select_related('source', 'stock')
        context['profile_change_form'] = ProfileChangeForm()
        context['email_and_name_change_form'] = EmailAndUsernameChangeForm(username=self.request.user.username, email=self.request.user.email)
        context['change_password_form'] = PasswordChangingForm(self.request.user)
        context['privacy_settings_form'] = PrivacySettingsForm(instance=self.request.user.profile.privacysettings)
        return context
