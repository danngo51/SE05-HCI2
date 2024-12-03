from django.shortcuts import render, get_object_or_404
from .models import Recipe, Tag, Ingredient, Nutrition

# Landing page view
def home(request):
    return render(request, 'recipes/home.html')

# View to display all recipes
def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

# View to display a single recipe's details
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    nutrition = recipe.nutrition if hasattr(recipe, 'nutrition') else None
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe, 'nutrition': nutrition})

# View to display all ingredients
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'recipes/ingredient_list.html', {'ingredients': ingredients})

# View to display all tags
def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'recipes/tag_list.html', {'tags': tags})

# View to display nutrition details for a recipe
def nutrition_detail(request, pk):
    nutrition = get_object_or_404(Nutrition, recipe__pk=pk)
    return render(request, 'recipes/nutrition_detail.html', {'nutrition': nutrition})
