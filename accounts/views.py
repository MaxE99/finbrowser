# Django imports
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic.detail import DetailView
# Local imports
from accounts.models import PrivacySettings, Profile, SocialLink
from home.models import HighlightedArticle, Source, List
from home.logic.pure_logic import paginator_create
from home.forms import AddListForm
from home.views import NotificationMixin, AddToListInfoMixin, CreateListFormMixin, AddExternalArticleFormMixin


class ProfileView(DetailView, NotificationMixin, AddToListInfoMixin, CreateListFormMixin, AddExternalArticleFormMixin):
    model = Profile
    context_object_name = 'profile'    
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        created_lists = List.objects.get_created_lists(profile.user).filter(is_public=True)
        subscribed_sources = Source.objects.get_subscribed_sources(profile.user)
        subscribed_lists = List.objects.get_subscribed_lists(profile.user)
        highlighted_articles = HighlightedArticle.objects.filter(user=profile.user).order_by('-article__pub_date')
        highlighted_articles, _ = paginator_create(self.request, highlighted_articles, 10)
        social_links = SocialLink.objects.filter(profile=profile)
        privacy_settings = get_object_or_404(PrivacySettings, profile=profile)
        context['created_lists'] = created_lists
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_lists'] = subscribed_lists
        context['highlighted_articles'] = highlighted_articles
        context['social_links'] = social_links
        context['privacy_settings'] = privacy_settings
        return context        


# def profile(request, slug):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             new_list.creator = request.user
#             new_list.save()
#             list_id = new_list.list_id
#             messages.success(request, f'List has been created!')
#             return redirect('home:list-details', list_id=list_id)
#     profile = get_object_or_404(Profile, slug=slug)
#     created_lists = List.objects.get_created_lists(
#         profile.user).filter(is_public=True)
#     subscribed_sources = Source.objects.get_subscribed_sources(profile.user)
#     subscribed_lists = List.objects.get_subscribed_lists(profile.user)
#     highlighted_articles = HighlightedArticle.objects.filter(
#         user=profile.user).order_by('-article__pub_date')
#     highlighted_articles, _ = paginator_create(request, highlighted_articles,
#                                                10)
#     add_list_form = AddListForm()
#     social_links = SocialLink.objects.filter(profile=profile)
#     if request.user.is_authenticated:
#         highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#             request.user)
#         user_lists = List.objects.get_created_lists(request.user)
#     else:
#         highlighted_articles_titles = None
#         user_lists = None
#     privacy_settings = get_object_or_404(PrivacySettings, profile=profile)
#     context = {
#         'add_list_form': add_list_form,
#         'profile': profile,
#         'created_lists': created_lists,
#         'subscribed_sources': subscribed_sources,
#         'subscribed_lists': subscribed_lists,
#         'highlighted_articles': highlighted_articles,
#         'social_links': social_links,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'user_lists': user_lists,
#         'privacy_settings': privacy_settings,
#     }
#     return render(request, 'accounts/profile.html', context)