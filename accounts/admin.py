from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.forms import CustomUserChangeForm, CustomUserCreationForm
from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ['email', 'is_staff', 'is_active']
    list_filter = ['email', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (None, {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_instructor', 'is_staff', 'is_active')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Advance Permissions', {'classes': ('collapse',), 'fields': ('groups', 'user_permissions')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_instructor', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
