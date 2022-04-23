# Django import
from django.shortcuts import render, get_object_or_404
# Local import
from home.models import (Source, Article, List, SourceRating,
                         HighlightedArticle)
from home.logic.pure_logic import paginator_create
from home.logic.selectors import website_logo_get


def profile(request, domain):
    source = get_object_or_404(Source, domain=domain)
    articles = Article.objects.filter(source=source).order_by('-pub_date')
    articles, _ = paginator_create(request, articles, 5)
    lists = List.objects.filter(
        sources__source_id=source.source_id).order_by('name')
    lists, _ = paginator_create(request, lists, 5)
    website_logo = website_logo_get(source.website)
    average_rating = SourceRating.objects.get_average_rating(source)
    ammount_of_ratings = SourceRating.objects.get_ammount_of_ratings(source)
    if request.user.is_authenticated:
        if request.user in source.subscribers.all():
            subscribed = True
        else:
            subscribed = False
        user_rating = SourceRating.objects.get_user_rating(
            request.user, source)
        highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
            request.user)
        user_lists = List.objects.get_created_lists(request.user)
    else:
        subscribed = False  # Refactoren
        user_rating = None
        highlighted_articles_titles = None
        user_lists = None
    context = {
        'ammount_of_ratings': ammount_of_ratings,
        'articles': articles,
        'lists': lists,
        'source': source,
        'website_logo': website_logo,
        'subscribed': subscribed,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists
    }
    return render(request, 'source/profile.html', context)
