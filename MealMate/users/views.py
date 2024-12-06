import os
from dotenv import load_dotenv
from pathlib import Path
from recipes.services import get_personalized_recommendations_with_health_concerns, get_personalized_recommendations_with_health_concerns_with_search

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the directory of the current script (main.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the full path to the .env file
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, EmailLoginForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# LLM
import random
from openai import OpenAI
import json
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key = API_KEY)

# Models 
from .models import UserProfile, Budget
from recipes.models import Recipe, RecipeRating


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('health_concerns')  # Redirect to the health_concerns
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = 'users/login.html'




class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change_form.html'
    success_url = '/profile/'

    def form_valid(self, form):
        messages.success(self.request, "Your password was successfully changed!")
        return super().form_valid(form)

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'users/profile_details.html',{'profile': profile})


@login_required
def history(request):
    user_ratings = RecipeRating.objects.filter(user=request.user).select_related('recipe')
    context = {
        'ratings': user_ratings,
    }
    return render(request, 'users/profile_history.html', context)


### PREFERENCES ###
@login_required
def health_concerns(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.health_concerns = existing_concerns + new_concerns
        profile.save()
        return redirect('budget')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_health_concerns.html', {
        'existing_data': profile.health_concerns or [],  # Existing concerns are locked
    })

@login_required
def budget(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)  # Get the current user's profile
    budgets = Budget.objects.all()  # Fetch all budgets
    selected_budget = profile.budget
    if request.method == 'POST':
        # Get the selected budget from POST data
        selected_budget_id = request.POST.get('budget')

        # Save the selected budget to the user's profile
        if selected_budget_id:
            try:
                selected_budget = Budget.objects.get(id=selected_budget_id)
                profile.budget = selected_budget
                profile.save()
            except Budget.DoesNotExist:
                # Handle the case where the budget ID is invalid
                pass

        return redirect('diet')  # Redirect to the next page
    
    return render(request, 'users/pref_budget.html', {
        'budgets': budgets,
        'selected_budget': selected_budget
    })

@login_required
def diet_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.diet = existing_concerns + new_concerns
        profile.save()
        return redirect('dishes')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_diet.html', {
        'existing_data': profile.diet or [],  # Existing concerns are locked
    })

@login_required
def dishes_preferences(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Get updated health concerns from POST data
        new_concerns = request.POST.getlist('new[]')
        existing_concerns = request.POST.getlist('existing[]')
        
        # Save updated concerns to the database
        profile.preferred_cuisines = existing_concerns + new_concerns
        profile.save()
        return redirect('done')  # Redirect to the next page

    # Pass existing health concerns to the template
    return render(request, 'users/pref_dishes.html', {
        'existing_data': profile.preferred_cuisines or [],  # Existing concerns are locked
    })

@login_required
def final_page(request):
    """
    Renders the final page with the button and handles button press logic (POST request).
    """
    if request.method == 'POST':
        return redirect('main')

    return render(request, 'users/pref_done.html')
    


### MAIN ###
@login_required
def main(request):
    # Get the search query and button click from the GET request
    search_query = request.GET.get('query', '').strip()
    button_clicked = request.GET.get('button', None)

    # Get user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    ### SEARCH BAR: FILTERING ###
    if button_clicked == "filter" and search_query:
        print("Filtering with search query")
        recipes = get_personalized_recommendations_with_health_concerns_with_search(profile, query=search_query, threshold_search=0.5)
        print(f"Filtered recipes: {recipes}")
    ### DEFAULT ###
    else:
        recipes = get_personalized_recommendations_with_health_concerns(profile)

    return render(request, 'users/main.html', {'recipes': recipes, 'search_query': search_query})


@login_required
def recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    time = [recipe.minutes // 60, recipe.minutes % 60]
    nutrition = recipe.nutrition if hasattr(recipe, 'nutrition') else None
    return render(request, 'users/recipe.html', {'recipe': recipe, 'nutrition': nutrition, 'time': time})

@login_required
def change_options(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)     # Get the current user's profile
    budgets = Budget.objects.all() 

    if request.method == 'POST':
        # Handle health concerns
        new_health_concerns = request.POST.getlist('new_hc[]')
        existing_health_concerns = request.POST.getlist('existing_hc[]')

        # Handle budget
        selected_budget_id = request.POST.get('budget')

        # Save the selected budget to the user's profile
        if selected_budget_id:
            try:
                selected_budget = Budget.objects.get(id=selected_budget_id)
                profile.budget = selected_budget
                profile.save()
            except Budget.DoesNotExist:
                # Handle the case where the budget ID is invalid
                pass

        # Handle diet styles
        new_diets = request.POST.getlist('new_diet[]')
        existing_diets = request.POST.getlist('existing_diet[]')

        # Handle preferences
        new_dishes = request.POST.getlist('new_dish[]')
        existing_dishes = request.POST.getlist('existing_dish[]')

        # Update the user's profile
        profile.health_concerns = existing_health_concerns + new_health_concerns
        profile.diet = existing_diets + new_diets
        profile.preferred_cuisines = existing_dishes + new_dishes
        profile.save()

        return redirect('main')  # Redirect to main page

    return render(request, 'users/change_options.html', {
        'existing_health_concerns': profile.health_concerns,
        'budgets': budgets,                     # List of budgets
        'selected_budget': profile.budget,      # Selected budget
        'existing_diets': profile.diet,
        'existing_dishes': profile.preferred_cuisines, 
    })

@login_required
def preferences(request):

    return render(request, 'users/profile_preferences.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from recipes.models import Recipe
from recipes.forms import RecipeRatingForm
from .services import handle_rating

@login_required
def recipe_test(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'POST':
        form = RecipeRatingForm(request.POST)
        if form.is_valid():
            rating_value = form.cleaned_data['rating']
            result = handle_rating(request.user, recipe.id, rating_value)
            messages.success(request, result['message'])
            return redirect('recipe_test', pk=pk)
    else:
        # Pre-fill the form if the user has already rated the recipe
        try:
            user_rating = RecipeRating.objects.get(user=request.user, recipe=recipe)
            form = RecipeRatingForm(initial={'rating': user_rating.rating})
        except RecipeRating.DoesNotExist:
            form = RecipeRatingForm()

    result = handle_rating(request.user, recipe.id)
    context = {
        'recipe': recipe,
        'form': form,
        'user_rating': result['rating'],
        'average_rating': result['average_rating'],
        'rating_count': result['rating_count'],
    }
    return render(request, 'users/recipe_test.html', context)

@login_required
def profile_ratings(request):
    user_ratings = RecipeRating.objects.filter(user=request.user).select_related('recipe')
    context = {
        'ratings': user_ratings,
    }
    return render(request, 'users/profile_ratings.html', context)

