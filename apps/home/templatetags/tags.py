# Django import
from django import template

register = template.Library()

@register.inclusion_tag('source/source_container.html')
def create_source_container(title, qs):
    return {'title': title, 'qs': qs}

@register.inclusion_tag('article/content_container.html')
def create_content_container(title, qs, request, user_lists, csrf_token, add_list_form, highlighted_content_ids):
    return {'title': title, 'qs': qs, 'request': request, 'user_lists': user_lists, 'csrf_token': csrf_token, 'add_list_form': add_list_form, 'highlighted_content_ids': highlighted_content_ids}

@register.inclusion_tag('article/fk_content_container.html')
def create_fk_content_container(title, qs, request, user_lists, csrf_token, add_list_form, highlighted_content_ids):
    return {'title': title, 'qs': qs, 'request': request, 'user_lists': user_lists, 'csrf_token': csrf_token, 'add_list_form': add_list_form, 'highlighted_content_ids': highlighted_content_ids}

@register.inclusion_tag('list/list_slider_container.html')
def create_list_slider_container(title, qs):
    return {'title': title, 'qs': qs}

@register.filter(name='check_inclusion')
def check_inclusion(qs1, qs2):
    for obj in qs1:
        if(str(obj.name) in qs2):
            return True
    return False

@register.filter(name='calc_ranking')
def calk_ranking(counter, page_rank):
    if page_rank == 1:
        return counter
    return counter + ((page_rank-1)*25)

@register.filter(name='check_has_rated')
def check_has_rated(source, user_ratings):
    rating = user_ratings.filter(source=source)
    if rating.exists():
        return rating.first().rating
    return False

@register.filter(name="check_param_selected")
def check_param_selected(params, args):
    if "," in args:
        key, value = args.split(',')
    else:
        key = "sector"
        value = args
    if not params or key not in params or value not in params[key]:
        return False
    return True


@register.filter(name="get_tags")
def get_tags(params):
    return params['tag']


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context['request'].GET.copy()
    for k, v in kwargs.items():
        query[k] = v
    return query.urlencode()