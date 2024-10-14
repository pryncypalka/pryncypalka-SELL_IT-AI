from django.db import models
from django.utils import timezone
from django.conf import settings


class ChatData(models.Model):
    prompt_id = models.CharField(max_length=255, primary_key=True, null=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    token_used = models.IntegerField(null=True)

    prompt_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.prompt_id
