from django.db import models
from pgvector.django import VectorField
from django.contrib.auth.models import User

# Create your models here.
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Recipe(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, related_name='recipes')  # Many-to-many with Tag
    minutes = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    n_ingredients = models.IntegerField(default=0)
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes')  # Many-to-many with Ingredient
    n_steps = models.IntegerField(default=0)
    instructions = models.JSONField(default=list)  # JSONField to store list of instructions
    
    def __str__(self):
        return self.title
    

class Nutrition(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name='nutrition', primary_key=True)  # One-to-One relationship with Recipe
    calories = models.FloatField(null=True, blank=True)
    total_fat = models.FloatField(null=True, blank=True)
    sugar = models.FloatField(null=True, blank=True)
    sodium = models.FloatField(null=True, blank=True)
    protein = models.FloatField(null=True, blank=True)
    saturated_fat = models.FloatField(null=True, blank=True)
    carbohydrates = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Nutrition for {self.recipe.title}"
    

class Embedded_Ingredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="embedded_ingredient")
    embedding = VectorField(dimensions=1536)


class Embedded_Recipe(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name="embedded_recipe")
    embedding = VectorField(dimensions=1536)


class RecipeRating(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    date_rated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  # A user can only rate a recipe once

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title} as {self.rating}"

