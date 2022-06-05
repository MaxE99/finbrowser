# Django imports
from django.shortcuts import get_object_or_404
from django.views.generic.detail import DetailView
# Local imports
from accounts.models import PrivacySettings, Profile, SocialLink
from home.models import HighlightedArticle, List, Source
from home.logic.pure_logic import paginator_create
from home.views import AddArticlesToListsMixin


class ProfileView(DetailView, AddArticlesToListsMixin):
    queryset = Profile.objects.select_related('user')
    context_object_name = 'profile'    
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        privacy_settings = get_object_or_404(PrivacySettings, profile=profile)
        context['created_lists'] = List.objects.get_created_lists(profile.user).filter(is_public=True)
        context['subscribed_sources'] = Source.objects.get_subscribed_sources(profile.user) if privacy_settings.subscribed_sources_public else None
        context['subscribed_lists'] = List.objects.get_subscribed_lists(profile.user) if privacy_settings.list_subscribtions_public else None
        context['highlighted_articles'] = paginator_create(self.request, HighlightedArticle.objects.filter(user=profile.user).select_related('article__source', 'article__source__sector').order_by('-article__pub_date'), 10) if privacy_settings.highlighted_articles_public else None
        context['social_links'] = SocialLink.objects.select_related('website').filter(profile=profile)
        return context        

