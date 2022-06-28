from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model

def validate_domain_available(username):
    from apps.accounts.models import Profile
    User = get_user_model()
    if Profile.objects.filter(slug=slugify(username)).exists() and User.objects.filter(username=username).exists() == False:
        raise ValidationError('This username is already taken!')