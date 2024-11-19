from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_cuisines = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    budget = models.TextField(blank=True)  
    dietary_needs = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username