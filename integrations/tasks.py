from celery import shared_task
from django.utils import timezone


@shared_task
def refresh_allegro_tokens():
   from .models import AllegroToken
   print("Starting token refresh...")
  
   expiring_soon = timezone.now() + timezone.timedelta(hours=1)
   tokens = AllegroToken.objects.filter(expires_at__lte=expiring_soon)
  
   print(f"Found {tokens.count()} tokens to refresh")
  
   for token in tokens:
       success = token.refresh_if_needed()
       print(f"Token refresh for user {token.user.username}: {'Success' if success else 'Failed'}")
  
   print("Token refresh completed")