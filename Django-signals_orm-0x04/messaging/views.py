from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import get_user_model

User = get_user_model()


@login_required
def delete_user(request):
    """Allow the authenticated user to delete their own account.

    Related data is cleaned up by the post_delete signal on the User model.
    """
    user = request.user
    user.delete()
    # Redirect to a generic homepage or goodbye page
    return redirect("/")
