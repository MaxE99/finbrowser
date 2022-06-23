from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

def validate_domain_available(username):
    from accounts.models import Profile
    if Profile.objects.filter(slug=slugify(username)).exists():
        raise ValidationError('This username is already taken!')