from django.db import models
from django.utils import timezone
from django.conf import settings
from .allegro_auth import AllegroAuth

def get_allegro_client():
    return AllegroAuth(
        client_id=settings.ALLEGRO_CLIENT_ID,
        client_secret=settings.ALLEGRO_CLIENT_SECRET,
        redirect_uri=settings.ALLEGRO_REDIRECT_URI,
        sandbox=settings.ALLEGRO_SANDBOX
    )
    
class AllegroToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='allegro_token')
    access_token = models.TextField()
    refresh_token = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def refresh_if_needed(self):
        if self.expires_at <= timezone.now() + timezone.timedelta(minutes=5):
            try:
                allegro = get_allegro_client()
                token_data = allegro.refresh_access_token(self.refresh_token)
                
                self.access_token = token_data['access_token']
                self.refresh_token = token_data['refresh_token']
                self.expires_at = timezone.now() + timezone.timedelta(seconds=token_data['expires_in'])
                self.save()
            except Exception:
                return False
        return True

    def is_valid(self):
        try:
            if self.refresh_if_needed():
                allegro = get_allegro_client()
                allegro.make_request('/me', access_token=self.access_token)
                return True
            return False
        except Exception:
            return False