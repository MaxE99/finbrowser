# Django import
from django import template

register = template.Library()

@register.inclusion_tag('source/source_container.html')
def create_source_container(title, qs):
    return {'title': title, 'qs': qs}

@register.inclusion_tag('article/content_container.html')
def create_content_container(title, qs, request, user_lists, csrf_token, add_list_form, highlighted_content_titles):
    return {'title': title, 'qs': qs, 'request': request, 'user_lists': user_lists, 'csrf_token': csrf_token, 'add_list_form': add_list_form, 'highlighted_content_titles': highlighted_content_titles}

@register.inclusion_tag('article/fk_content_container.html')
def create_fk_content_container(title, qs, request, user_lists, csrf_token, add_list_form, highlighted_content_titles):
    return {'title': title, 'qs': qs, 'request': request, 'user_lists': user_lists, 'csrf_token': csrf_token, 'add_list_form': add_list_form, 'highlighted_content_titles': highlighted_content_titles}

@register.inclusion_tag('list/list_slider_container.html')
def create_list_slider_container(title, qs):
    return {'title': title, 'qs': qs}