from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _


CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    ordering = ('id',)
    list_display = ('email', 'username')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('username',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password1', 'password2')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
