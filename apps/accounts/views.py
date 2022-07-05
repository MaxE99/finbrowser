# Django imports
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseRedirect
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.accounts.forms import EmailAndUsernameChangeForm, PasswordChangingForm, ProfileChangeForm, PrivacySettingsForm
from apps.mixins import BaseMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.accounts.models import PrivacySettings, Profile, SocialLink
from apps.article.models import HighlightedArticle
from apps.list.models import List
from apps.source.models import Source
from apps.accounts.models import SocialLink, Website
from apps.home.models import Notification


class ProfileView(DetailView, BaseMixin):
    queryset = Profile.objects.select_related('user')
    context_object_name = 'profile'    
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        privacy_settings = get_object_or_404(PrivacySettings, profile=profile)
        context['social_links'] = SocialLink.objects.filter(profile=profile).select_related('website').defer("website__url", "website__favicon", "website__name")
        context['highlighted_articles'] = paginator_create(self.request, HighlightedArticle.objects.get_highlighted_articles_of_user(profile.user), 10) if privacy_settings.highlighted_articles_public else None
        context['created_lists'] = List.objects.filter(creator=profile.user, is_public=True).select_related('creator__profile').order_by('name').only('slug', 'list_pic', 'name', 'creator__profile')
        context['subscribed_lists'] = List.objects.get_subscribed_lists(profile.user) if privacy_settings.list_subscribtions_public else None
        context['subscribed_sources'] = Source.objects.get_subscribed_sources(profile.user) if privacy_settings.subscribed_sources_public else None
        return context        


class SettingsView(LoginRequiredMixin, TemplateView, BaseMixin):
    template_name = 'accounts/settings.html'

    def post(self, request, *args, **kwargs):
        if 'changeProfileForm' in request.POST:
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
        context['websites'] = Website.objects.all()
        context['social_links'] = SocialLink.objects.select_related('website').filter(profile=self.request.user.profile)
        context['notifications'] = Notification.objects.select_related('source', 'list', 'list__creator__profile').filter(user=self.request.user)
        context['profile_change_form'] = ProfileChangeForm()
        context['email_and_name_change_form'] = EmailAndUsernameChangeForm(username=self.request.user.username, email=self.request.user.email)
        context['change_password_form'] = PasswordChangingForm(self.request.user)
        context['privacy_settings_form'] = PrivacySettingsForm(instance=self.request.user.profile.privacysettings)
        return context
