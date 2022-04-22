# Django imports
from django.shortcuts import render, get_object_or_404
# Local imports
from accounts.models import Profile, SocialLink
from home.models import HighlightedArticle, Source, List
from home.logic.pure_logic import paginator_create


def profile(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    created_lists = List.objects.get_created_lists(profile.user)
    subscribed_sources = Source.objects.get_subscribed_sources(profile.user)
    subscribed_lists = List.objects.get_subscribed_lists(profile.user)
    highlighted_articles = HighlightedArticle.objects.filter(
        user=profile.user).order_by('-article__pub_date')
    highlighted_articles, _ = paginator_create(request, highlighted_articles,
                                               10)
    social_links = SocialLink.objects.filter(profile=profile)
    context = {
        'profile': profile,
        'created_lists': created_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_lists': subscribed_lists,
        'highlighted_articles': highlighted_articles,
        'social_links': social_links
    }
    return render(request, 'accounts/profile.html', context)