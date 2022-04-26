# Django import
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# Local import
from home.models import (Notification, Source, Article, List, SourceRating,
                         HighlightedArticle)
from home.logic.pure_logic import paginator_create
from home.logic.selectors import website_logo_get
from home.forms import AddListForm


def profile(request, domain):
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            new_list = add_list_form.save(commit=False)
            new_list.creator = request.user
            new_list.save()
            list_id = new_list.list_id
            messages.success(request, f'List has been created!')
            return redirect('home:list-details', list_id=list_id)
    source = get_object_or_404(Source, domain=domain)
    latest_articles = Article.objects.filter(
        source=source).order_by('-pub_date')
    latest_articles, _ = paginator_create(request, latest_articles, 10,
                                          'latest_articles')
    lists = List.objects.filter(sources__source_id=source.source_id).filter(
        is_public=True).order_by('name')
    lists, _ = paginator_create(request, lists, 10, 'lists')
    website_logo = website_logo_get(source.website)
    average_rating = SourceRating.objects.get_average_rating(source)
    ammount_of_ratings = SourceRating.objects.get_ammount_of_ratings(source)
    add_list_form = AddListForm()
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
        notifications_activated = Notification.objects.filter(
            user=request.user, source=source).exists()
    else:
        subscribed = False  # Refactoren
        user_rating = None
        highlighted_articles_titles = None
        user_lists = None
        notifications_activated = None
    context = {
        'add_list_form': add_list_form,
        'ammount_of_ratings': ammount_of_ratings,
        'latest_articles': latest_articles,
        'lists': lists,
        'source': source,
        'website_logo': website_logo,
        'subscribed': subscribed,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists,
        'notifications_activated': notifications_activated
    }
    return render(request, 'source/profile.html', context)
