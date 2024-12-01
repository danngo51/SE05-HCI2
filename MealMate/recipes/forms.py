from django import forms
from .models import Recipe, Ingredient

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 'image']


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']  # Fields to include in the form