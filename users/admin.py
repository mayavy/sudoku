from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
# from django.utils.translation import gettext, gettext_lazy as _


class UserAdminConfig(UserAdmin):
    ordering = ('-date_joined',)  # - controls ascending dsecending
    list_display = ('username', 'email', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(CustomUser, UserAdminConfig)
