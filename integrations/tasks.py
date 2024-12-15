from celery import shared_task
from django.utils import timezone


@shared_task
def refresh_allegro_tokens():
   from .models import AllegroToken
  
   expiring_soon = timezone.now() + timezone.timedelta(hours=1)
   tokens = AllegroToken.objects.filter(expires_at__lte=expiring_soon)
  
   for token in tokens:
       success = token.refresh_if_needed()
  
