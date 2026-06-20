"""Admin configuration for users application."""

from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for users."""

    list_display = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for subscriptions."""

    list_display = (
        'user',
        'author',
    )
