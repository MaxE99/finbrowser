# Django imports
from django.urls import path
# Local imports
from home.api.api import (
     FilteredList, FilteredSite, FilteredSourceForLists,
    FilteredSource, FilteredSourceForFeed, FilteredListForFeed,
    FilteredArticles, list_change_subscribtion_status, source_change_subscribtion_status,
    delete_source_from_list, delete_list, sources_add, source_rate, list_rate,
    article_highlight, lists_add_article, profile_add_website_link,
    profile_pic_delete, profile_banner_delete, social_link_delete,
    social_links_add, notification_change_source, notification_change_list,
    social_link_change, delete_article_from_list)

app_name = 'api'

urlpatterns = [
    path('list_change_subscribtion_status/<int:list_id>',
         list_change_subscribtion_status),
    path('source_change_subscribtion_status/<str:domain>',
         source_change_subscribtion_status),
    path('search_sources_for_list/<int:list_id>/<str:search_term>',
         FilteredSourceForLists.as_view()),
    path('search_lists/<str:search_term>', FilteredList.as_view()),
    path('search_site/<str:search_term>', FilteredSite.as_view()),
    path('delete_source_from_list/<int:list_id>/<str:source>',
         delete_source_from_list),
    path('delete_list/<int:list_id>', delete_list),
    path('add_sources/<str:sources>/<int:list_id>', sources_add),
    path('rate_source/<str:source>/<int:rating>', source_rate),
    path('rate_list/<int:list_id>/<int:rating>', list_rate),
    path('highlight_article/<int:article_id>', article_highlight),
    path('add_article_to_lists/<int:article_id>/<str:list_ids>',
         lists_add_article),
    path('profile_add_website_link/<str:website>/<str:link>',
         profile_add_website_link),
    path('delete_profile_pic', profile_pic_delete),
    path('delete_profile_banner', profile_banner_delete),
    path('delete_social_link/<str:website>', social_link_delete),
    path('add_social_links/<str:website>/<path:url>', social_links_add),
    path('search_sources/<str:search_term>', FilteredSource.as_view()),
    path('filter_sources_from_feed/<str:search_term>',
         FilteredSourceForFeed.as_view()),
    path('filter_lists_from_feed/<str:search_term>',
         FilteredListForFeed.as_view()),
    path('change_source_notification/<int:source_id>',
         notification_change_source),
    path('change_list_notification/<int:list_id>', notification_change_list),
    path('search_articles/<str:search_term>', FilteredArticles.as_view()),
    path('change_social_link/<str:website>/<path:new_link>',
         social_link_change),
    path('delete_article_from_list/<int:list_id>/<int:article_id>',
         delete_article_from_list)
]