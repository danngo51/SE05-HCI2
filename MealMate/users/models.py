from django.db import models
from django.contrib.auth.models import User
from pgvector.django import VectorField


# Create your models here.
class Budget(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Example: "Low Budget", "Medium Budget", "High Budget"
    min_value = models.DecimalField(max_digits=10, decimal_places=2)  # Minimum budget value
    max_value = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum budget value

    class Meta:
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"  # Optional metadata

    def __str__(self):
        return f"{self.name} ({self.min_value} - {self.max_value})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    health_concerns = models.JSONField(blank=True, default=dict)  
    budget = models.ForeignKey(Budget, null=True, blank=True, on_delete=models.SET_NULL)      # on_delete means that if the budget is deleted from the budget table, the user's budget will be set to NULL
    diet = models.JSONField(blank=True, default=dict)          
    preferred_cuisines = models.JSONField(blank=True, default=dict)  
    embedding = VectorField(dimensions=1536, null=True, blank=True)  # Vector field for user embedding

    def __str__(self):
        return self.user.username
