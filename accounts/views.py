# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
# Local imports
from accounts.models import Profile, SocialLink
from home.models import HighlightedArticle, Source, List
from home.logic.pure_logic import paginator_create
from home.forms import AddListForm


def profile(request, slug):
    if 'createListForm' in request.POST:
        add_list_form = AddListForm(request.POST, request.FILES)
        if add_list_form.is_valid():
            add_list_form.save()
            messages.success(request, f'List has been created!')
            return redirect('home:feed')
    profile = get_object_or_404(Profile, slug=slug)
    created_lists = List.objects.get_created_lists(
        profile.user).filter(is_public=True)
    subscribed_sources = Source.objects.get_subscribed_sources(profile.user)
    subscribed_lists = List.objects.get_subscribed_lists(profile.user)
    highlighted_articles = HighlightedArticle.objects.filter(
        user=profile.user).order_by('-article__pub_date')
    highlighted_articles, _ = paginator_create(request, highlighted_articles,
                                               10)
    add_list_form = AddListForm()
    social_links = SocialLink.objects.filter(profile=profile)
    if request.user.is_authenticated:
        highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
            request.user)
        user_lists = List.objects.get_created_lists(request.user)
    else:
        highlighted_articles_titles = None
        user_lists = None
    context = {
        'add_list_form': add_list_form,
        'profile': profile,
        'created_lists': created_lists,
        'subscribed_sources': subscribed_sources,
        'subscribed_lists': subscribed_lists,
        'highlighted_articles': highlighted_articles,
        'social_links': social_links,
        'highlighted_articles_titles': highlighted_articles_titles,
        'user_lists': user_lists,
    }
    return render(request, 'accounts/profile.html', context)