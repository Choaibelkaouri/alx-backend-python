from django.contrib import admin

from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "receiver", "short_content", "timestamp", "edited", "read")
    list_filter = ("edited", "read", "timestamp")
    search_fields = ("sender__username", "receiver__username", "content")

    def short_content(self, obj):
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "message", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username",)


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "edited_by", "edited_at", "short_old_content")
    list_filter = ("edited_at",)
    search_fields = ("message__content", "old_content", "edited_by__username")

    def short_old_content(self, obj):
        return (obj.old_content[:50] + "...") if len(obj.old_content) > 50 else obj.old_content
