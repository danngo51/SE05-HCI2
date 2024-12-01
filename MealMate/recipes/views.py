from django.shortcuts import render, get_object_or_404, redirect
from .models import Recipe, Ingredient
from .forms import RecipeForm, IngredientForm

# Create your views here.
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.created_by = request.user
            recipe.save()
            form.save_m2m()
            return redirect('recipe_list')
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

def recipe_list(request):
    recipes = Recipe.objects.all()  # Fetch all recipes
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)  # Fetch a single recipe by primary key (id)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

def ingredient_create(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new ingredient to the database
            return redirect('ingredient_list')  # Redirect to a page showing ingredients (create this later)
    else:
        form = IngredientForm()
    return render(request, 'recipes/ingredient_form.html', {'form': form})

def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'recipes/ingredient_list.html', {'ingredients': ingredients})
