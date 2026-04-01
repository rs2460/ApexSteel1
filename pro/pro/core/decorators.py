from django.contrib.auth.decorators import user_passes_test

def superuser_required(view_func):
    """Decorator for views that checks that the user is a superuser."""
    decorated_view = user_passes_test(
        lambda u: u.is_superuser,
        login_url='/login/' # Or your custom login URL
    )
    return decorated_view(view_func)
