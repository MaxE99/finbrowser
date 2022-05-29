from regex import R
from home.models import Notification, NotificationMessage

def get_notifications(request):
    if request.user.is_authenticated:
        notifications_subscribtions = Notification.objects.filter(user=request.user)
        unseen_notifications = NotificationMessage.objects.filter(notification__in=notifications_subscribtions, user_has_seen=False).count()
        source_notifications_subscribtions = Notification.objects.filter(user=request.user, source__isnull=False)
        source_notifications = NotificationMessage.objects.filter(notification__in=source_notifications_subscribtions).select_related('article', 'article__source').order_by('-date')  
        list_notifications_subscribtions = Notification.objects.filter(user=request.user, list__isnull=False)
        list_notifications = NotificationMessage.objects.filter(notification__in=list_notifications_subscribtions).select_related('article', 'article__source').order_by('-date')
    else:
        unseen_notifications = source_notifications = list_notifications = None
    return {'unseen_notifications': unseen_notifications, 'source_notifications':source_notifications , 'list_notifications':list_notifications}

