# Django imports
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import get_user_model
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
# Python imports
from datetime import timedelta, date
# Local imports
from accounts.models import SocialLink, Website
from home.models import Article, HighlightedArticle, List, Sector, Source, ListRating, ExternalSource, Notification
from home.forms import AddListForm, ListPicChangeForm, ListNameChangeForm, AddExternalArticleForm
from home.logic.pure_logic import paginator_create
from home.logic.selectors import notifications_get
from accounts.forms import EmailAndUsernameChangeForm, PasswordChangingForm, ProfileChangeForm, PrivacySettingsForm

User = get_user_model()


# Mixins:

class NotificationMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            unseen_notifications, source_notifications, list_notifications = notifications_get(self.request.user)
        else:
            unseen_notifications = source_notifications = list_notifications = None
        context['unseen_notifications'] = unseen_notifications
        context['source_notifications'] = source_notifications
        context['list_notifications'] = list_notifications
        return context


class AddToListInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['highlighted_articles_titles'] = HighlightedArticle.objects.get_highlighted_articles_title(self.request.user)
            context['user_lists'] = List.objects.get_created_lists(self.request.user)
        else:
            context['highlighted_articles_titles'] = None
            context['user_lists'] = None
        return context


class CreateListFormMixin(FormMixin):
    form_class = AddListForm

    def post(self, request, *args, **kwargs):
        form = AddListForm(request.POST, request.FILES)
        multi_form_page = True if 'multi_form_page' in kwargs else False
        if form.is_valid():
            new_list = form.save(commit=False)
            if List.objects.filter(name=new_list.name, creator=self.request.user).exists():
                messages.error(self.request, 'You have already created a list with this name!')
                return "Failed" if multi_form_page else redirect('home:lists')
            else:
                new_list.creator = self.request.user
                new_list.save()
                profile_slug = new_list.creator.profile.slug
                list_slug = new_list.slug
                messages.success(self.request, 'List has been created!')
                return [profile_slug, list_slug] if multi_form_page else redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_list_form'] = AddListForm()
        return context


class AddArticlesToListsMixin(AddToListInfoMixin, CreateListFormMixin):
    """Both Mixins are almost always used together"""


class AddExternalArticleFormMixin(FormMixin):
    form_class = AddExternalArticleForm

    def post(self, request, *args, **kwargs):
        add_external_articles_form = AddExternalArticleForm(request.POST)
        if add_external_articles_form.is_valid():
            data = add_external_articles_form.cleaned_data
            website_name = data['website_name']
            sector = data['sector']
            title = data['title']
            link = data['link']
            pub_date = data['pub_date']
            external_source = ExternalSource.objects.create(user=request.user, website_name=website_name).sector.add(sector)
            external_source.sector.add(sector)
            article = Article.objects.create(title=title, link=link, pub_date=pub_date, external_source=external_source)
            HighlightedArticle.objects.create(user=request.user, article=article)
            messages.success(request, 'Article has been added!')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_external_articles_form'] = AddExternalArticleForm()
        return context


# Views:

class SectorView(ListView, NotificationMixin):
    model = Sector
    context_object_name = 'sectors'
    template_name = 'home/sectors.html'
    queryset = Sector.objects.all().order_by('name')


class ListsView(ListView, NotificationMixin, CreateListFormMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    queryset = List.objects.filter(is_public=True).order_by('name')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(List.objects.filter(is_public=True))
        return context


class ArticleView(ListView, NotificationMixin, AddArticlesToListsMixin):
    model = Article
    context_object_name = 'search_articles'
    template_name = 'home/articles.html'
    queryset = Article.objects.filter(external_source=None).order_by('-pub_date')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(Article.objects.filter(external_source=None))
        context['sectors'] = Sector.objects.all().order_by('name')
        return context


class MainView(TemplateView, NotificationMixin):
    template_name = 'home/main.html'


class SectorDetailView(DetailView, NotificationMixin, AddArticlesToListsMixin):
    model = Sector
    context_object_name = 'sector'
    template_name = 'home/sector_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sector = self.get_object()
        sources = sector.sectors.all().filter(top_source=True)
        context['articles_from_sector'] = paginator_create(self.request, Article.objects.get_articles_from_sector(sector).order_by('-pub_date'), 10, 'articles_from_sector')
        context['articles_from_top_sources'] = paginator_create(self.request, Article.objects.filter(source__in=sources).order_by('-pub_date'), 10, 'articles_from_top_sources')
        return context


class FeedView(TemplateView, LoginRequiredMixin, NotificationMixin, AddArticlesToListsMixin, AddExternalArticleFormMixin):
    template_name = 'home/feed.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST:
            post_res = CreateListFormMixin.post(self, request, multi_form_page=True)
            if post_res == 'Failed':
                return redirect('home:feed')
            else:
                profile_slug, list_slug = post_res
                return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'addExternalArticlesForm' in request.POST:
            AddExternalArticleFormMixin.post(self, request)
            return redirect('home:feed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_sources = Source.objects.get_subscribed_sources(self.request.user)
        context['user_lists'] = List.objects.get_created_lists(self.request.user)
        context['subscribed_lists'] = List.objects.get_subscribed_lists(self.request.user)
        context['subscribed_sources'] = subscribed_sources
        context['subscribed_articles'] = paginator_create(self.request, Article.objects.get_articles_from_subscribed_sources(subscribed_sources), 10, 'subscribed_articles')
        context['highlighted_articles'] = paginator_create(self.request, HighlightedArticle.objects.filter(user=self.request.user).order_by('-article__pub_date'), 10, 'highlighted_articles')
        return context


class SearchResultView(TemplateView, NotificationMixin, AddArticlesToListsMixin):
    template_name = 'home/search_results.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = kwargs['search_term']
        context['filtered_lists'] = paginator_create(self.request, List.objects.filter_lists(search_term), 10, 'filtered_lists')
        context['filtered_sources'] = Source.objects.filter_sources(search_term)
        context['filtered_articles'] = paginator_create(self.request, Article.objects.filter_articles(search_term), 10, 'filtered_articles')
        return context


class ListSearchView(ListView, NotificationMixin, AddArticlesToListsMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    paginate_by = 10

    def get_queryset(self):
        timeframe = self.kwargs['timeframe']
        content_type = self.kwargs['content_type']
        minimum_rating = self.kwargs['minimum_rating']
        sources = self.kwargs['sources']
        filter_args = {'main_website_source': sources}
        if timeframe != 'All' and timeframe != None:
            filter_args['updated_at__gte'] = date.today() - timedelta(
                days=int(timeframe))
        filter_args = dict(
            (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
        lists = List.objects.filter(**filter_args).filter(
            is_public=True).order_by('name')
        ##########################################################################
        # filter content_type
        if content_type != 'All':
            exclude_list = []
            if content_type == "Articles":
                for list in lists:
                    if len(list.articles.all()) <= len(list.sources.all()):
                        exclude_list.append(list)
                        # lists.exclude(list_id=list.list_id)
            else:
                for list in lists:
                    if len(list.articles.all()) >= len(list.sources.all()):
                        exclude_list.append(list)
                        # lists.exclude(list_id=list.list_id)
            if len(exclude_list):
                for list in exclude_list:
                    lists = lists.exclude(list_id=list.list_id)

        # filter minimum_rating
        exclude_list = []
        if minimum_rating != 'All' and minimum_rating is not None:
            minimum_rating = float(minimum_rating)
            for list in lists:
                if list.get_average_rating != "None":
                    if list.get_average_rating < minimum_rating:
                        exclude_list.append(list)
                else:
                    exclude_list.append(list)
        if len(exclude_list):
            for list in exclude_list:
                lists = lists.exclude(list_id=list.list_id)
        return lists

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(self.get_queryset())
        return context


class ArticleSearchView(ListView, NotificationMixin, AddArticlesToListsMixin):
    model = Article
    context_object_name = 'search_articles'
    template_name = 'home/articles.html'
    paginate_by = 10

    def get_queryset(self):
        timeframe = self.kwargs['timeframe']
        sector = self.kwargs['sector']
        paywall = self.kwargs['paywall']
        sources = self.kwargs['sources']
        filter_args = {'source__paywall': paywall, 'source__website': sources}
        if timeframe != 'All' and timeframe != None:
            filter_args['pub_date__gte'] = date.today() - timedelta(
                days=int(timeframe))
        filter_args = dict(
            (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
        search_articles = Article.objects.filter(external_source=None).filter(
            **filter_args).order_by('-pub_date')
        notloesung_search_articles = []
        if sector != 'All' and sector != None:
            # Refactoring necceseary
            sector = Sector.objects.get(name=sector)
            for x in search_articles:
                all_sectors = x.source.sector.all()
                if all_sectors.filter(name=str(sector)):
                    notloesung_search_articles.append(x)
        if notloesung_search_articles:
            search_articles = notloesung_search_articles
        return search_articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = len(self.get_queryset())
        context['sectors'] = Sector.objects.all().order_by('name')
        return context


class ListDetailView(TemplateView, NotificationMixin, AddArticlesToListsMixin):
    model = List
    context_object_name = 'list'
    template_name = 'home/list_details.html'

    def post(self, request, *args, **kwargs):
        if 'createListForm' in request.POST:
            post_res = CreateListFormMixin.post(self, request, multi_form_page=True)
            if post_res == 'Failed':
                return redirect('home:feed')
            else:
                profile_slug, list_slug = post_res
                return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'changeListForm' in request.POST:
            profile_slug = self.request.path_info.rsplit('/', 2)[-2]
            list_slug = self.request.path_info.rsplit('/', 1)[-1]
            list = get_object_or_404(List, slug=list_slug)
            if self.request.user == list.creator:
                change_list_name_form = ListNameChangeForm(request.POST, instance=list)
                change_list_pic_form = ListPicChangeForm(request.POST, request.FILES, instance=list)
                new_list_slug = slugify(request.POST.get('name'))
                if change_list_pic_form.is_valid:
                    change_list_pic_form.save()
                if change_list_name_form.is_valid and List.objects.filter(creator=request.user, slug=new_list_slug).exists() == False:
                    change_list_name_form.save()
                else:
                    messages.error(request, "Error: You can't use this name!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug != list_slug:
                    return redirect('home:list-details', profile_slug=profile_slug , list_slug=new_list_slug)
                else:
                    return HttpResponseRedirect(self.request.path_info)
            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        list = get_object_or_404(List, slug=self.kwargs['list_slug'])
        list_id = list.list_id
        if self.request.user.is_authenticated:
            notifications_activated = Notification.objects.filter(user=self.request.user, list=list).exists()
            subscribed = True if self.request.user in list.subscribers.all() else False
            user_rating = ListRating.objects.get_user_rating(self.request.user, list_id)
        else:
            notifications_activated = user_rating = None
            subscribed = False  
        context['list'] = list
        context['latest_articles'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources(list), 10, 'latest_articles') 
        context['highlighted_articles'] = paginator_create(self.request, List.objects.get_highlighted_articles(list.list_id), 10, 'highlighted_articles')
        context['ammount_of_ratings'] = ListRating.objects.get_ammount_of_ratings(list_id)
        context['average_rating'] = ListRating.objects.get_average_rating(list_id)
        context['notifications_activated'] = notifications_activated
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        if self.request.user == list.creator:
            context['change_list_pic_form'] = ListPicChangeForm()
            context['change_list_name_form'] = ListNameChangeForm()
        return context


class SettingsView(TemplateView, LoginRequiredMixin, NotificationMixin):
    template_name = 'home/settings.html'

    def post(self, request, *args, **kwargs):
        if 'changeProfileForm' in request.POST:
            email_and_name_change_form = EmailAndUsernameChangeForm(request.POST, username=request.user.username, email=request.user.email, instance=request.user)
            profile_change_form = ProfileChangeForm(request.POST, request.FILES, bio=request.user.profile.bio, instance=request.user.profile)
            if profile_change_form.is_valid():
                profile_change_form.save()
                if email_and_name_change_form.is_valid():
                    request.user.save()
                    request.user.profile.save()
                    return HttpResponseRedirect(self.request.path_info)
                else:
                    messages.error(request, "Error: Username or email already exists!")
        elif "changePasswordForm" in request.POST:
            change_password_form = PasswordChangingForm(user=request.user, data=request.POST or None)
            if change_password_form.is_valid():
                change_password_form.save()
                update_session_auth_hash(request, change_password_form.user)
                return HttpResponseRedirect(self.request.path_info)
        elif 'changePrivacySettingsForm' in request.POST:
            privacy_settings_form = PrivacySettingsForm(request.POST, instance=request.user.profile.privacysettings)
            if privacy_settings_form.is_valid():
                form = privacy_settings_form.save(commit=False)
                form.profile = request.user.profile
                form.save()
                return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['websites'] = Website.objects.all()
        context['social_links'] = SocialLink.objects.filter(profile=self.request.user.profile)
        context['notifications'] = Notification.objects.filter(user=self.request.user)
        context['profile_change_form'] = ProfileChangeForm(bio=self.request.user.profile.bio)
        context['email_and_name_change_form'] = EmailAndUsernameChangeForm(username=self.request.user.username, email=self.request.user.email)
        context['change_password_form'] = PasswordChangingForm(self.request.user)
        context['privacy_settings_form'] = PrivacySettingsForm(instance=self.request.user.profile.privacysettings)
        return context


####################################################################################################################################


# def sectors(request):
#     sectors = Sector.objects.all().order_by('name')
#     if request.user.is_authenticated:
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     return render(request, 'home/sectors.html', {
#         'sectors': sectors, 
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications
#         })

# def lists(request):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     lists = List.objects.filter(is_public=True).order_by('name')
#     add_list_form = AddListForm()
#     results_found = len(lists)
#     lists, _ = paginator_create(request, lists, 10)
#     if request.user.is_authenticated:
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     return render(
#         request, 'home/lists.html', {
#             'add_list_form': add_list_form,
#             'lists': lists,
#             'results_found': results_found,
#             'unseen_notifications': unseen_notifications,
#             'source_notifications': source_notifications,
#             'list_notifications': list_notifications,
#         })

# def articles(request):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     search_articles = Article.objects.filter(external_source=None).order_by('-pub_date')
#     results_found = len(search_articles)
#     search_articles, _ = paginator_create(request, search_articles, 10)
#     sectors = Sector.objects.all().order_by('name')
#     if request.user.is_authenticated:
#         highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#             request.user)
#         user_lists = List.objects.get_created_lists(request.user)
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         highlighted_articles_titles = None
#         user_lists = None
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     add_list_form = AddListForm()
#     context = {
#         'add_list_form': add_list_form,
#         'results_found': results_found,
#         'search_articles': search_articles,
#         'sectors': sectors,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'user_lists': user_lists,
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/articles.html', context)

# def main(request):
#     if request.user.is_authenticated:
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     context = {
#         'unseen_notifications': unseen_notifications, 
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/main.html', context)


# def sector_details(request, slug):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     sector = get_object_or_404(Sector, slug=slug)
#     articles_from_sector = Article.objects.get_articles_from_sector(sector)
#     articles_from_sector, _ = paginator_create(request, articles_from_sector,
#                                                10)
#     sources = sector.sectors.all().filter(top_source=True)
#     articles_from_top_sources = Article.objects.filter(
#         source__in=sources).order_by('-pub_date')
#     articles_from_top_sources, _ = paginator_create(request,
#                                                     articles_from_top_sources,
#                                                     10)
#     add_list_form = AddListForm()
#     if request.user.is_authenticated:
#         highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#             request.user)
#         user_lists = List.objects.get_created_lists(request.user)
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         highlighted_articles_titles = None
#         user_lists = None
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     context = {
#         'add_list_form': add_list_form,
#         'articles_from_top_sources': articles_from_top_sources,
#         'articles_from_sector': articles_from_sector,
#         'sector': sector,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'user_lists': user_lists,
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/sector_details.html', context)

# @login_required()
# def feed(request):
#     unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     elif 'addExternalArticlesForm' in request.POST:
#         add_external_articles_form = AddExternalArticleForm(request.POST)
#         if add_external_articles_form.is_valid():
#             data = add_external_articles_form.cleaned_data
#             website_name = data['website_name']
#             sector = data['sector']
#             title = data['title']
#             link = data['link']
#             pub_date = data['pub_date']
#             external_source = ExternalSource.objects.create(
#                 user=request.user, website_name=website_name)
#             external_source.sector.add(sector)
#             article = Article.objects.create(title=title,
#                                              link=link,
#                                              pub_date=pub_date,
#                                              external_source=external_source)
#             HighlightedArticle.objects.create(user=request.user,
#                                               article=article)
#             messages.success(request, 'Article has been added!')
#             return redirect('home:feed')
#     user_lists = List.objects.get_created_lists(request.user)
#     subscribed_lists = List.objects.get_subscribed_lists(request.user)
#     subscribed_sources = Source.objects.get_subscribed_sources(request.user)
#     subscribed_articles = Article.objects.get_articles_from_subscribed_sources(
#         subscribed_sources)
#     subscribed_articles, _ = paginator_create(request, subscribed_articles, 10,
#                                               'subscribed_articles')
#     highlighted_articles = HighlightedArticle.objects.filter(
#         user=request.user).order_by('-article__pub_date')
#     highlighted_articles, _ = paginator_create(request, highlighted_articles,
#                                                10, 'highlighted_articles')
#     add_list_form = AddListForm()
#     add_external_articles_form = AddExternalArticleForm()
#     highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#         request.user)
#     context = {
#         'add_list_form': add_list_form,
#         'add_external_articles_form': add_external_articles_form,
#         'user_lists': user_lists,
#         'subscribed_lists': subscribed_lists,
#         'subscribed_sources': subscribed_sources,
#         'subscribed_articles': subscribed_articles,
#         'highlighted_articles': highlighted_articles,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/feed.html', context)

# def search_results(request, search_term):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     filtered_lists = List.objects.filter_lists(search_term)
#     filtered_lists, _ = paginator_create(request, filtered_lists, 10,
#                                          'filtered_lists')
#     filtered_sources = Source.objects.filter_sources(search_term)
#     filtered_articles = Article.objects.filter_articles(search_term)
#     filtered_articles, _ = paginator_create(request, filtered_articles, 10,
#                                             'filtered_articles')
#     add_list_form = AddListForm()
#     if request.user.is_authenticated:
#         highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#             request.user)
#         user_lists = List.objects.get_created_lists(request.user)
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         highlighted_articles_titles = None
#         user_lists = None
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     context = {
#         'add_list_form': add_list_form,
#         'filtered_articles': filtered_articles,
#         'filtered_lists': filtered_lists,
#         'filtered_sources': filtered_sources,
#         'search_term': search_term,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'user_lists': user_lists, 
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/search_results.html', context)

# def lists_search(request, timeframe, content_type, minimum_rating, sources):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     filter_args = {'main_website_source': sources}
#     if timeframe != 'All' and timeframe != None:
#         filter_args['updated_at__gte'] = date.today() - timedelta(
#             days=int(timeframe))
#     filter_args = dict(
#         (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
#     lists = List.objects.filter(**filter_args).filter(
#         is_public=True).order_by('name')
#     ##########################################################################
#     # filter content_type
#     if content_type != 'All':
#         exclude_list = []
#         if content_type == "Articles":
#             for list in lists:
#                 if len(list.articles.all()) <= len(list.sources.all()):
#                     exclude_list.append(list)
#                     # lists.exclude(list_id=list.list_id)
#         else:
#             for list in lists:
#                 if len(list.articles.all()) >= len(list.sources.all()):
#                     exclude_list.append(list)
#                     # lists.exclude(list_id=list.list_id)
#         if len(exclude_list):
#             for list in exclude_list:
#                 lists = lists.exclude(list_id=list.list_id)

#     # filter minimum_rating
#     exclude_list = []
#     if minimum_rating != 'All' and minimum_rating is not None:
#         minimum_rating = float(minimum_rating)
#         for list in lists:
#             if list.get_average_rating != "None":
#                 if list.get_average_rating < minimum_rating:
#                     exclude_list.append(list)
#             else:
#                 exclude_list.append(list)
#     if len(exclude_list):
#         for list in exclude_list:
#             lists = lists.exclude(list_id=list.list_id)
#     ##########################################################################
#     add_list_form = AddListForm()
#     results_found = len(lists)
#     lists, _ = paginator_create(request, lists, 10)
#     if request.user.is_authenticated:
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     else:
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     return render(
#         request, 'home/lists.html', {
#             'add_list_form': add_list_form,
#             'lists': lists,
#             'results_found': results_found,
#             'unseen_notifications': unseen_notifications,
#             'source_notifications': source_notifications,
#             'list_notifications': list_notifications,
#         })

# def articles_search(request, timeframe, sector, paywall, sources):
#     if 'createListForm' in request.POST:
#         add_list_form = AddListForm(request.POST, request.FILES)
#         if add_list_form.is_valid():
#             new_list = add_list_form.save(commit=False)
#             if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                 messages.error(request, 'You already have crated a list with this name!')
#             else:
#                 new_list.creator = request.user
#                 new_list.save()
#                 profile_slug = new_list.creator.profile.slug
#                 list_slug = new_list.slug
#                 messages.success(request, 'List has been created!')
#                 return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#     filter_args = {'source__paywall': paywall, 'source__website': sources}
#     if timeframe != 'All' and timeframe != None:
#         filter_args['pub_date__gte'] = date.today() - timedelta(
#             days=int(timeframe))
#     filter_args = dict(
#         (k, v) for k, v in filter_args.items() if v is not None and v != 'All')
#     search_articles = Article.objects.filter(external_source=None).filter(
#         **filter_args).order_by('-pub_date')
#     notloesung_search_articles = []
#     if sector != 'All' and sector != None:
#         # Refactoring necceseary
#         sector = Sector.objects.get(name=sector)
#         for x in search_articles:
#             all_sectors = x.source.sector.all()
#             if all_sectors.filter(name=str(sector)):
#                 notloesung_search_articles.append(x)
#     if notloesung_search_articles:
#         search_articles = notloesung_search_articles
#         # Refactoring necceseary
#     results_found = len(search_articles)
#     search_articles, _ = paginator_create(request, search_articles, 10)
#     sectors = Sector.objects.all().order_by('name')
#     if request.user.is_authenticated:
#         unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#         highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#             request.user)
#         user_lists = List.objects.get_created_lists(request.user)
#     else:
#         highlighted_articles_titles = None
#         user_lists = None
#         unseen_notifications = None
#         source_notifications = None
#         list_notifications = None
#     add_list_form = AddListForm()
#     context = {
#         'add_list_form': add_list_form,
#         'results_found': results_found,
#         'search_articles': search_articles,
#         'sectors': sectors,
#         'highlighted_articles_titles': highlighted_articles_titles,
#         'user_lists': user_lists,
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#     }
#     return render(request, 'home/articles.html', context)   

# def list_details(request, profile_slug, list_slug):
#     list = get_object_or_404(List, slug=list_slug)
#     if list.creator == request.user or list.is_public == True:
#         if request.method == 'POST':
#             if 'changeListForm' in request.POST:
#                 change_list_name_form = ListNameChangeForm(request.POST)
#                 change_list_pic_form = ListPicChangeForm(request.POST,
#                                                          request.FILES)
#                 if change_list_pic_form.is_valid:
#                     change_list_pic_form.save()
#                 if change_list_name_form.is_valid:
#                     change_list_name_form.save()
#                 return redirect('home:list-details', profile_slug=profile_slug , list_slug=list_slug)
#             elif 'createListForm' in request.POST:
#                 add_list_form = AddListForm(request.POST, request.FILES)
#                 if add_list_form.is_valid():
#                     new_list = add_list_form.save(commit=False)
#                     if List.objects.filter(name=new_list.name, creator=request.user).exists():
#                         messages.error(request, 'You already have crated a list with this name!')
#                     else:
#                         new_list.creator = request.user
#                         new_list.save()
#                         profile_slug = new_list.creator.profile.slug
#                         list_slug = new_list.slug
#                         messages.success(request, 'List has been created!')
#                         return redirect('home:list-details', profile_slug=profile_slug, list_slug=list_slug)
#         latest_articles = Article.objects.get_articles_from_list_sources(list)
#         latest_articles, _ = paginator_create(request, latest_articles, 10,
#                                               'latest_articles')
#         change_list_pic_form = ListPicChangeForm()
#         change_list_name_form = ListNameChangeForm()
#         list_id = list.list_id
#         ammount_of_ratings = ListRating.objects.get_ammount_of_ratings(list_id)
#         average_rating = ListRating.objects.get_average_rating(list_id)
#         highlighted_articles = List.objects.get_highlighted_articles(list_id)
#         highlighted_articles, _ = paginator_create(request,
#                                                    highlighted_articles, 10,
#                                                    'highlighted_articles')
#         add_list_form = AddListForm()
#         if request.user.is_authenticated:
#             unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#             highlighted_articles_titles = HighlightedArticle.objects.get_highlighted_articles_title(
#                 request.user)
#             user_lists = List.objects.get_created_lists(request.user)
#             notifications_activated = Notification.objects.filter(
#                 user=request.user, list=list).exists()
#             if request.user in list.subscribers.all():
#                 subscribed = True
#             else:
#                 subscribed = False
#             user_rating = ListRating.objects.get_user_rating(
#                 request.user, list_id)
#         else:
#             highlighted_articles_titles = None
#             user_lists = None
#             subscribed = False  # Refactoren
#             user_rating = None
#             notifications_activated = None
#             unseen_notifications = None
#             list_notifications = None
#             source_notifications = None
#         context = {
#             'add_list_form': add_list_form,
#             'ammount_of_ratings': ammount_of_ratings,
#             'change_list_name_form': change_list_name_form,
#             'change_list_pic_form': change_list_pic_form,
#             'list': list,
#             'subscribed': subscribed,
#             'latest_articles': latest_articles,
#             'average_rating': average_rating,
#             'user_rating': user_rating,
#             'highlighted_articles': highlighted_articles,
#             'highlighted_articles_titles': highlighted_articles_titles,
#             'user_lists': user_lists,
#             'notifications_activated': notifications_activated,
#             'unseen_notifications': unseen_notifications,
#             'source_notifications': source_notifications,
#             'list_notifications': list_notifications,
#         }
#         return render(request, 'home/list_details.html', context)
#     else:
#         raise Http404("This list does not exist!")

# @login_required()
# def settings(request):
#     unseen_notifications, source_notifications, list_notifications = notifications_get(request.user)
#     if request.method == "POST":
#         if 'changeProfileForm' in request.POST:
#             email_and_name_change_form = EmailAndUsernameChangeForm(
#                 request.POST,
#                 username=request.user.username,
#                 email=request.user.email,
#                 instance=request.user)
#             profile_change_form = ProfileChangeForm(
#                 request.POST,
#                 request.FILES,
#                 bio=request.user.profile.bio,
#                 instance=request.user.profile)
#             if profile_change_form.is_valid():
#                 profile_change_form.save()
#                 if email_and_name_change_form.is_valid():
#                     request.user.save()
#                     request.user.profile.save()
#                     return redirect('../../settings/')
#                 else:
#                     messages.error(request,
#                                    "Error: Username or email already exists!")
#         elif "changePasswordForm" in request.POST:
#             change_password_form = PasswordChangingForm(user=request.user,
#                                                         data=request.POST
#                                                         or None)
#             if change_password_form.is_valid():
#                 change_password_form.save()
#                 update_session_auth_hash(request, change_password_form.user)
#                 return redirect('home:settings')
#         elif 'changePrivacySettingsForm' in request.POST:
#             privacy_settings_form = PrivacySettingsForm(
#                 request.POST, instance=request.user.profile.privacysettings)
#             if privacy_settings_form.is_valid():
#                 form = privacy_settings_form.save(commit=False)
#                 form.profile = request.user.profile
#                 form.save()
#                 return redirect('home:settings')
#     profile_change_form = ProfileChangeForm(bio=request.user.profile.bio)
#     email_and_name_change_form = EmailAndUsernameChangeForm(
#         username=request.user.username, email=request.user.email)
#     change_password_form = PasswordChangingForm(request.user)
#     websites = Website.objects.all()
#     social_links = SocialLink.objects.filter(profile=request.user.profile)
#     privacy_settings_form = PrivacySettingsForm(
#         instance=request.user.profile.privacysettings)
#     notifications = Notification.objects.filter(user=request.user)
#     context = {
#         'change_password_form': change_password_form,
#         'email_and_name_change_form': email_and_name_change_form,
#         'profile_change_form': profile_change_form,
#         'social_links': social_links,
#         'websites': websites,
#         'privacy_settings_form': privacy_settings_form,
#         'unseen_notifications': unseen_notifications,
#         'source_notifications': source_notifications,
#         'list_notifications': list_notifications,
#         'notifications': notifications
#     }
#     return render(request, 'home/settings.html', context)