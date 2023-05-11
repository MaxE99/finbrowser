# Django import
from django import template
from django.utils import timezone

# Python imports
from datetime import timedelta


register = template.Library()


@register.inclusion_tag("source/source_container.html")
def create_source_container(sources, subscribed_sources, request):
    return {
        "sources": sources,
        "subscribed_sources": subscribed_sources,
        "request": request,
    }


@register.inclusion_tag("article/content_container.html")
def create_content_container(
    qs,
    request,
    highlighted_content_ids,
    qs_name,
):
    return {
        "qs": qs,
        "request": request,
        "highlighted_content_ids": highlighted_content_ids,
        "qs_name": qs_name,
    }


@register.inclusion_tag("article/fk_content_container.html")
def create_fk_content_container(
    qs,
    request,
    highlighted_content_ids,
    qs_name,
):
    return {
        "qs": qs,
        "request": request,
        "highlighted_content_ids": highlighted_content_ids,
        "qs_name": qs_name,
    }


@register.filter(name="calc_ranking")
def calc_ranking(counter, page_rank):
    if page_rank == 1:
        return counter
    return counter + ((page_rank - 1) * 25)


@register.filter(name="check_has_rated")
def check_has_rated(source, user_ratings):
    if source.source_id in user_ratings.keys():
        return user_ratings[source.source_id]
    return False


@register.filter(name="check_param_selected")
def check_param_selected(params, args):
    if "," in args:
        key, value = args.split(",")
    else:
        key = "sector"
        value = args
    if not params or key not in params or value not in params[key]:
        return False
    return True


@register.filter(name="get_tags")
def get_tags(params):
    return params["tag"]


@register.filter(name="get_source_ids_in_list")
def get_source_ids_in_list(params):
    return list(params.values_list("source_id", flat=True))


@register.filter(name="get_article_ids_in_list")
def get_article_ids_in_list(params):
    return list(params.values_list("article_id", flat=True))


@register.filter(name="get_time_since_last_content_published")
def get_time_since_last_content_published(params):
    if params is None:
        return None
    diff = timezone.now() - params
    if diff < timedelta(minutes=1):
        # some (chinese) website give the date not in UTC
        if diff.seconds < 0:
            return "5 minutes ago"
        return "now"
    if diff < timedelta(hours=1):
        return f"{diff.seconds // 60} minutes ago"
    if diff < timedelta(days=1):
        return f"{diff.seconds // 3600} hours ago"
    else:
        return f"{diff.days} days ago"


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
