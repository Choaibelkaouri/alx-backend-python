from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page

from messaging.models import Message

User = get_user_model()


@login_required
def conversation_thread(request, username):
    """Display a threaded conversation between the current user and another user.

    Uses select_related and prefetch_related to optimize queries for messages and replies.
    """
    other_user = get_object_or_404(User, username=username)

    # Base messages in the conversation (top-level messages only)
    messages = (
        Message.objects.filter(
            sender__in=[request.user, other_user],
            receiver__in=[request.user, other_user],
            parent_message__isnull=True,
        )
        .select_related("sender", "receiver")
        .prefetch_related("replies", "replies__sender", "replies__receiver")
        .order_by("timestamp")
    )

    context = {
        "other_user": other_user,
        "messages": messages,
    }
    return render(request, "chats/conversation_thread.html", context)


def _get_all_replies(message):
    """Recursively collect all replies to a message.

    This is a Python-level recursion that can be used to render
    threads in templates.
    """
    all_replies = []
    for reply in message.replies.all():
        all_replies.append(reply)
        all_replies.extend(_get_all_replies(reply))
    return all_replies


@login_required
def unread_inbox(request):
    """Example view that uses the custom unread manager for the current user."""
    unread_messages = Message.unread.for_user(request.user)
    context = {"messages": unread_messages}
    return render(request, "chats/unread_inbox.html", context)


@cache_page(60)
@login_required
def conversation_list(request):
    """Cached view that lists recent conversations/messages for the user.

    The view is cached for 60 seconds using @cache_page.
    """
    recent_messages = (
        Message.objects.filter(receiver=request.user)
        .select_related("sender")
        .only("id", "sender", "content", "timestamp")
        .order_by("-timestamp")[:50]
    )
    context = {"messages": recent_messages}
    return render(request, "chats/conversation_list.html", context)
