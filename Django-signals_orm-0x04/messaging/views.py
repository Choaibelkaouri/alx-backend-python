from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model

from .models import Message

User = get_user_model()


@login_required
def delete_user(request):
    """
    View katkhlli l-user yms7 compte dyalo.
    Cleanup dyal data kayt3emel bih post_delete signal 3la User.
    """
    user = request.user
    user.delete()
    return redirect("/")


@login_required
def conversation_thread(request, username):
    """
    Threaded conversation bin request.user o user okhor (username).
    Hna kanst3emlou Message.objects.filter + select_related + prefetch_related
    باش noptimiziw queries dyal messages o replies.
    """
    other_user = get_object_or_404(User, username=username)

    # Messages f had conversation (top-level only: parent_message null)
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
    Recursive query b Django ORM باش njebou جميع replies dyal message.
    N9dro nst3emlou had function f templates wla views باش ndisplayiw thread kaml.
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
