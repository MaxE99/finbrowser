# Django Imports
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Local imports
from apps.accounts.forms import UserCreationForm, UserChangeForm
from apps.accounts.models import Profile, Website, PrivacySettings

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ('username', 'email')
    list_filter = ('username', )
    fieldsets = ((None, {'fields': ('email', 'password')}), )
    add_fieldsets = ((None, {
        'classes': ('wide', ),
        'fields': ('username', 'email', 'password1', 'password2'),
    }), )
    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(Website)
admin.site.register(PrivacySettings)
admin.site.unregister(Group)