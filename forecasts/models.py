from django.db import models
from django.conf import settings
from django.utils import timezone



class Location(models.Model):
    zipcode = models.CharField(max_length=10)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.zipcode

    def save(self, *args, **kwargs):
        return super(Location, self).save(*args, **kwargs)
