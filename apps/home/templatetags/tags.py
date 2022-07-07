# Django import
from django import template

register = template.Library()

@register.inclusion_tag('source/source_container.html')
def create_source_container(title, qs):
    return {'title': title, 'qs': qs}

@register.inclusion_tag('article/article_container.html')
def create_article_container(title, qs, request):
    return {'title': title, 'qs': qs, 'request': request}

@register.inclusion_tag('article/fk_article_container.html')
def create_fk_article_container(title, qs, request):
    return {'title': title, 'qs': qs, 'request': request}

@register.inclusion_tag('article/tweets_container.html')
def create_tweets_container(title, qs, request):
    return {'title': title, 'qs': qs, 'request': request}

@register.inclusion_tag('article/fk_tweets_container.html')
def create_fk_tweets_container(title, qs, request):
    return {'title': title, 'qs': qs, 'request': request}

@register.inclusion_tag('list/list_slider_container.html')
def create_list_slider_container(title, qs):
    return {'title': title, 'qs': qs}