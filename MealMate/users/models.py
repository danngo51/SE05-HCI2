from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    health_concerns = models.JSONField(blank=True, default=dict)  
    budget = models.JSONField(blank=True, default=dict)       
    diet = models.JSONField(blank=True, default=dict)          
    preferred_cuisines = models.JSONField(blank=True, default=dict)       

    def __str__(self):
        return self.user.username