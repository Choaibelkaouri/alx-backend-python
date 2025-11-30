from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page  # 👈 مهم

from .models import Message

User = get_user_model()


@login_required
def delete_user(request):
    """
    Allow the authenticated user to delete their own account.
    Related data is cleaned up by post_delete signal on User.
    """
    user = request.user
    user.delete()
    return redirect("/")


@cache_page(60)  # 👈 cache view dyal conversation list for 60 seconds
@login_required
def conversation_thread(request, username):
    """
    Threaded conversation between request.user and another user.
    Uses Message.objects.filter + select_related + prefetch_related
    to optimize messages and their replies.
    This view is cached for 60 seconds using cache_page.
    """
    other_user = get_object_or_404(User, username=username)

    # Base queryset: top-level messages in conversation
    messages_qs_1 = Message.objects.filter(
        sender=request.user,
        receiver=other_user,
        parent_message__isnull=True,
    )
    messages_qs_2 = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        parent_message__isnull=True,
    )

    messages = (
        messages_qs_1 | messages_qs_2
    ).select_related(
        "sender", "receiver"
    ).prefetch_related(
        "replies", "replies__sender", "replies__receiver"
    ).order_by("timestamp")

    context = {
        "other_user": other_user,
        "messages": messages,
    }
    return render(request, "messaging/conversation_thread.html", context)


def get_all_replies(message):
    """
    Recursive ORM-based helper to fetch all replies for a message.
    """
    replies = (
        Message.objects.filter(parent_message=message)
        .select_related("sender", "receiver")
        .prefetch_related("replies")
        .order_by("timestamp")
    )

    all_replies = []
    for reply in replies:
        all_replies.append(reply)
        all_replies.extend(get_all_replies(reply))
    return all_replies


@login_required
def unread_inbox(request):
    """
    Use the custom UnreadMessagesManager to get only unread messages
    for the current user, optimized with .only().
    """
    unread_messages = (
        Message.unread.unread_for_user(request.user)  # 👈 custom manager
        .only("id", "sender", "receiver", "content", "timestamp")  # 👈 .only() optimization
    )
    context = {"messages": unread_messages}
    return render(request, "messaging/unread_inbox.html", context)
