from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from apps.accounts.forms import UserChangeForm, UserCreationForm
from apps.accounts.models import Profile, Website

User = get_user_model()


class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the User model.

    This class extends the default Django UserAdmin to use custom forms
    for adding and changing users (UserCreationForm and UserChangeForm).
    It also customizes the list display, filters, fieldsets, search fields,
    and ordering for the User model in the admin interface.
    """

    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ("username", "email")
    list_filter = ("username",)
    fieldsets = ((None, {"fields": ("email", "password")}),)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Website)
admin.site.unregister(Group)
