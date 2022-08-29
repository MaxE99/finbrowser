# Django imports
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
# Local imports
from apps.list.forms import AddListForm
from apps.home.forms import KeywordNotificationCreationForm
from apps.article.models import HighlightedArticle
from apps.list.models import List
from apps.home.models import Notification, NotificationMessage


class AddToListInfoMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['highlighted_content_ids'] = HighlightedArticle.objects.get_highlighted_articles_ids(self.request.user)
            context['user_lists'] = List.objects.get_created_lists(self.request.user)
        else:
            context['highlighted_content_ids'] = None
            context['user_lists'] = None
        return context


class NotificationMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            notifications_subscribtions = Notification.objects.filter(user=self.request.user)
            unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications_subscribtions, user_has_seen=False).count()
            source_notifications_subscribtions = Notification.objects.filter(user=self.request.user, source__isnull=False)
            source_notifications = NotificationMessage.objects.filter(notification__in=source_notifications_subscribtions).select_related('article', 'article__source', 'article__source__website', 'article__tweet_type').order_by('-date')  
            list_notifications_subscribtions = Notification.objects.filter(user=self.request.user, list__isnull=False)
            list_notifications = NotificationMessage.objects.filter(notification__in=list_notifications_subscribtions).select_related('article', 'article__source', 'article__source__website', 'article__tweet_type').order_by('-date')  
            keyword_notifications_subscribtions = Notification.objects.filter(user=self.request.user, keyword__isnull=False)
            keyword_notifications = NotificationMessage.objects.filter(notification__in=keyword_notifications_subscribtions).select_related('article', 'article__source', 'article__source__website', 'article__tweet_type').order_by('-date')  
        else:
            unseen_notifications = source_notifications = list_notifications = keyword_notifications = None
        context['unseen_notifications'] = unseen_notifications
        context['source_notifications'] = source_notifications
        context['list_notifications'] = list_notifications
        context['keyword_notifications'] = keyword_notifications
        return context


class BaseFormMixins(FormMixin):
    form_class = AddListForm

    def post(self, request, *args, **kwargs):
        multi_form_page = True if 'multi_form_page' in kwargs else False
        if 'createListForm' in request.POST:
            form = AddListForm(request.POST, request.FILES)
            if form.is_valid():
                new_list = form.save(commit=False)
                if self.request.user.is_authenticated is False:
                    messages.error(self.request, 'Only registered users can create lists!')
                    return "Failed" if multi_form_page else redirect('list:lists')
                elif List.objects.filter(name=new_list.name, creator=self.request.user).exists() or List.objects.filter(slug=slugify(new_list.name), creator=self.request.user).exists():
                    messages.error(self.request, 'You have already created a list with that name!')
                    return "Failed" if multi_form_page else redirect('list:lists')
                else:
                    new_list.creator = self.request.user
                    new_list.save()
                    profile_slug = new_list.creator.profile.slug
                    list_slug = new_list.slug
                    messages.success(self.request, 'List has been created!')
                    return [profile_slug, list_slug] if multi_form_page else redirect('list:list-details', profile_slug=profile_slug, list_slug=list_slug)
            else:
                messages.error(request, "Currently only PNG and JPG files are supported!")
                return "Failed" if multi_form_page else HttpResponseRedirect(self.request.path_info)
        elif 'createKeywordNotificationForm' in request.POST:
            form = KeywordNotificationCreationForm(request.POST, request=request)
            if form.is_valid():
                form.save()
                return "Notification created" if multi_form_page else HttpResponseRedirect(self.request.path_info)
            else:
                if "You have already created a keyword with this term!" in str(form):
                    messages.error(request, "You have already created a keyword with this term!")
                else:
                    messages.error(request, "Keyword must consist of at least 3 characters!")
                return "Failed" if multi_form_page else HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_list_form'] = AddListForm()
        context['keyword_notification_creation_form'] = KeywordNotificationCreationForm()
        return context


class BaseMixin(AddToListInfoMixin, BaseFormMixins, NotificationMixin):
    """All 3 Mixins are required for notifications to work on every site"""
