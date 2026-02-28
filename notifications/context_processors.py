from typing import Dict


def unread_counts(request) -> Dict:
    """Provide unread notification counts for templates.

    Returns:
        dict with keys `unread_notifications` and `unread_chat_count` (ints).
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'unread_notifications': 0, 'unread_chat_count': 0}

    try:
        from .models import Notification
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        unread_chat = Notification.objects.filter(
            user=request.user, is_read=False, kind=Notification.Kind.CHAT_MESSAGE
        ).count()
        return {'unread_notifications': unread, 'unread_chat_count': unread_chat}
    except Exception:
        return {'unread_notifications': 0, 'unread_chat_count': 0}
