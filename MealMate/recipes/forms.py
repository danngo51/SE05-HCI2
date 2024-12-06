from django import forms
from .models import RecipeRating

class RecipeRatingForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect,
        }
