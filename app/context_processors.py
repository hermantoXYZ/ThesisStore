from .models import CallForReviewer


def pending_reviewer_count(request):
    """Inject pending reviewer application count for admin sidebar badge."""
    count = 0
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        try:
            count = CallForReviewer.objects.filter(status='pending').count()
        except Exception:
            pass
    return {'pending_reviewer_count': count}

