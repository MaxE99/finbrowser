# Django imports
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
# Local imports
from apps.logic.pure_logic import paginator_create
from apps.mixins import BaseMixin, CreateListFormMixin
from apps.list.forms import ListNameChangeForm, ListPicChangeForm
from apps.list.models import List, ListRating
from apps.home.models import Notification
from apps.article.models import Article
from apps.accounts.models import Website
from apps.base_logger import logger
from apps.logic.pure_logic import lists_filter

try:
    TWITTER = get_object_or_404(Website, name="Twitter")
except:
    logger.error("Twitter not found! Problem with database")
    TWITTER = None


class ListsView(ListView, BaseMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    queryset = List.objects.select_related('creator__profile').prefetch_related('articles', 'sources').filter(is_public=True).order_by('name')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = self.queryset.count()
        return context

class ListSearchView(ListView, BaseMixin):
    model = List
    context_object_name = 'lists'
    template_name = 'home/lists.html'
    paginate_by = 10

    def get_queryset(self):
        return lists_filter(self.kwargs['timeframe'], self.kwargs['content_type'], self.kwargs['minimum_rating'], self.kwargs['primary_source'], List.objects.filter(is_public=True).order_by('name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results_found'] = self.get_queryset().count()
        return context


class ListDetailView(TemplateView, BaseMixin):
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
                return redirect('list:lists-details', profile_slug=profile_slug, list_slug=list_slug)
        elif 'changeListForm' in request.POST:
            profile_slug = self.request.path_info.rsplit('/', 2)[-2]
            list_slug = self.request.path_info.rsplit('/', 1)[-1]
            list = get_object_or_404(List, slug=list_slug)
            if self.request.user == list.creator:
                new_list_slug = slugify(request.POST.get('name'))
                change_list_name_form = ListNameChangeForm(request.POST, instance=list)
                change_list_pic_form = ListPicChangeForm(request.POST, request.FILES, instance=list)
                if change_list_pic_form.is_valid():
                    change_list_pic_form.save()
                else:
                    messages.error(request, "Error: Currently only PNG and JPG files are supported!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug == list_slug:
                    messages.success(request, 'List settings have been saved!')
                elif change_list_name_form.is_valid() and new_list_slug != list_slug and List.objects.filter(creator=request.user, slug=new_list_slug).exists() == False:
                        change_list_name_form.save()
                        messages.success(request, 'List settings have been saved!')
                else:
                    messages.error(request, "Error: You've already created a list with that name!")
                    return HttpResponseRedirect(self.request.path_info)
                if new_list_slug != list_slug:
                    return redirect('list:lists-details', profile_slug=profile_slug , list_slug=new_list_slug)
                else:
                    return HttpResponseRedirect(self.request.path_info)
            else:
                logger.error(f'User tried to change list name of list created by another user! - {self.request.user}')
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
        context['latest_articles'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources_excluding_website(list, TWITTER), 10, 'latest_articles') 
        context['highlighted_articles'] = paginator_create(self.request, List.objects.get_highlighted_content_from_list_excluding_website(list_id, TWITTER), 10, 'highlighted_articles')
        context['notifications_activated'] = notifications_activated
        context['subscribed'] = subscribed
        context['user_rating'] = user_rating
        context['highlighted_tweets'] = paginator_create(self.request, List.objects.get_highlighted_content_from_list_and_website(list_id, TWITTER), 20, 'highlighted_tweets')
        context['newest_tweets'] = paginator_create(self.request, Article.objects.get_articles_from_list_sources_and_website(list, TWITTER), 20, 'newest_tweets')
        if self.request.user == list.creator:
            context['change_list_pic_form'] = ListPicChangeForm()
            context['change_list_name_form'] = ListNameChangeForm()
        return context
