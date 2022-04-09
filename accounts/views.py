# Django imports
from django.shortcuts import render, get_object_or_404
# Local imports
from accounts.models import Profile
from home.models import Source, List, Article
from home.logic.pure_logic import paginator_create


def profile(request, slug):
    profile = get_object_or_404(Profile, slug=slug)
    created_lists = List.objects.filter(creator=profile.user)
    subscribed_sources = Source.objects.filter(subscribers=profile.user)
    subscribed_lists = List.objects.filter(subscribers=profile.user)
    # Highlighted Articles are currently subscribed articles => I must change this
    highlighted_articles = Article.objects.filter(
        source__in=subscribed_sources).order_by('-pub_date')
    highlighted_articles, _ = paginator_create(request, highlighted_articles,
                                               7)
    # Highlighted Articles are currently subscribed articles => I must change this
    context = {
        'profile': profile,
        'created_lists': created_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_lists': subscribed_lists,
        'highlighted_articles': highlighted_articles
    }
    return render(request, 'accounts/profile.html', context)