# Django imports
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
# Local imports
from accounts.models import PrivacySettings, Profile, SocialLink
from home.models import HighlightedArticle, Source, List
from home.logic.pure_logic import paginator_create
from home.views import AddArticlesToListsMixin


class ProfileView(DetailView, AddArticlesToListsMixin):
    queryset = Profile.objects.select_related('user')
    context_object_name = 'profile'    
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['created_lists'] = List.objects.get_created_lists(profile.user).filter(is_public=True)
        context['subscribed_sources'] = Source.objects.get_subscribed_sources(profile.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(profile.user)
        context['highlighted_articles'] = paginator_create(self.request, HighlightedArticle.objects.select_related('source').filter(user=profile.user).order_by('-article__pub_date'), 10)
        context['social_links'] = SocialLink.objects.select_related('website').filter(profile=profile)
        context['privacy_settings'] = get_object_or_404(PrivacySettings, profile=profile)
        return context        

