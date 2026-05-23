from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "username", "email", "is_verified", "preferred_language", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_verified", "preferred_language")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("phone", "address", "avatar", "preferred_language", "is_verified")}),
    )
