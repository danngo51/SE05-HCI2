import os
from dotenv import load_dotenv
from pathlib import Path

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
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from users.services import generate_user_profile_embedding

from django.http import JsonResponse

# LLM
import random
from openai import OpenAI
import json
API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key = API_KEY)

# Models 
from .models import UserProfile, Budget
from recipes.models import Recipe, Nutrition


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)  # Automatically log in the user after registration
            return redirect('frontpage')  # Redirect to the front page
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = 'users/login.html'

@login_required
def profile(request):
    return render(request, 'users/profile_details.html')

@login_required
def preferences(request):
    return render(request, 'users/profile_preferences.html')

@login_required
def history(request):
    return render(request, 'users/profile_history.html')


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
        generate_user_profile_embedding(request)
        return redirect('main')

    return render(request, 'users/pref_done.html')
    


### MAIN ###
@login_required
def main(request):
    # search_query = request.GET.get('query', '').strip()
    # button_clicked = request.GET.get('button', None)

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    ## Get preferences
    preferences = {
        "health_concerns": profile.health_concerns,
        "budget": profile.budget,
        "diet": profile.diet,
        "preferred_dishes": profile.preferred_cuisines,
    }

    meal_data = list(Recipe.objects.all().order_by('id')[:2000])
    meal_ids = [meal.id for meal in meal_data]
    nutrition_data = list(Nutrition.objects.filter(recipe__in=meal_ids).all())
    # meal_data = list(Recipe.objects.values("id", "title", "ingredients", "tags"))
    # nutrition_data = list(Nutrition.objects.values("recipe", "calories", "total_fat", "sugar", "sodium", "protein", "saturated_fat", "carbohydrates"))

    # Combine data
    nutrition_map = {nutrition.recipe: nutrition for nutrition in nutrition_data}
    combined_data = [
        {
            "id": meal.id,
            "title": meal.title,
            "ingredients": meal.ingredients,
            "tags": meal.tags,
            "calories": nutrition_map[meal.id].calories if meal.id in nutrition_map else None,
            "total_fat": nutrition_map[meal.id].total_fat if meal.id in nutrition_map else None,
            "sugar": nutrition_map[meal.id].sugar if meal.id in nutrition_map else None,
            "sodium": nutrition_map[meal.id].sodium if meal.id in nutrition_map else None,
            "protein": nutrition_map[meal.id].protein if meal.id in nutrition_map else None,
            "saturated_fat": nutrition_map[meal.id].saturated_fat if meal.id in nutrition_map else None,
            "carbohydrates": nutrition_map[meal.id].carbohydrates if meal.id in nutrition_map else None,
        }
        for meal in meal_data
    ]

    ### SEARCH BAR: FILTERING ###
    # if button_clicked == "filter" and search_query:
    ### DEFAULT ###
    # else:
    formatted_prompt = "\n".join(
        f"title: {item['title']}, ingredients: {item['ingredients']}, tags: {item['tags']}, "
        f"calories: {item['calories']}, total_fat: {item['total_fat']}, sugar: {item['sugar']}, sodium: {item['sodium']}, "
        f"protein: {item['protein']}, saturated_fat: {item['saturated_fat']}, carbohydrates: {item['carbohydrates']}"
        for item in combined_data
    )

    # OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a meal recommender. You pick random meals from the list of meals I gave you based on user preferences by referring to the meal information. \
                                            Your response should be only the title of 3 meals (e.g. [meal title1, meal title2, ... etc]). \
                                            The provided meal titles must never be altered from the information I gave it to you.\
                                            Please prioritize filtering in the order of health concerns, budget, and other preferences."},
            {"role": "user", "content": (f"Suggests meals by referring to the meal information (ingredients, tags, nutritions) to incorporate user preferences (health_concerns, budget, diet, preferred dishes):\n{preferences}\n"
                                        f"The meals information including their nutritional information (calories, total_fat, sugar, sodium, protein, saturated_fat, carbohydrates) are:\n{formatted_prompt}" 
                                        f"Return only matching meal titles as a list.")},
        ]
    )
    print(response.choices)
    meals = [choice.message.content for choice in response.choices][0].strip("[]").split(", ")
    meals_dict = {}
    TAG_COLORS = ["#A7C957", "#F2E8DF", "#ffca7d", "#ffdd6c"]
    TAG_EXCLUDE_LIST = ['time-to-make', 'course', 'main-ingredient', 'cuisine', 'preparation', 'occasion', 'equipment']

    for meal in meals:
        recipe = Recipe.objects.get(title=meal)
        recipe_id = recipe.id
        minutes = recipe.minutes
        hours = minutes // 60
        remaining_minutes = minutes % 60 
        tags = recipe.tags.all()
        tags_list = [tag.name for tag in tags if tag.name not in TAG_EXCLUDE_LIST]
        tags_list = random.sample(tags_list, min(10, len(tags_list)))
        meals_dict[meal] = [recipe_id, hours, remaining_minutes, tags_list]

    meals_dict_with_colors = {}
    for title, meal_info in meals_dict.items():
        meals_dict_with_colors[title] = [
            {"id": meal_info[0], "hours": meal_info[1], "remaining_minutes": meal_info[2], "tag": tag, "color": TAG_COLORS[i % len(TAG_COLORS)]} for i, tag in enumerate(meal_info[3])
        ]

    return render(request, 'users/main.html', {"meals_dict": meals_dict_with_colors})

@login_required
def recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    time = [recipe.minutes // 60, recipe.minutes % 60]
    nutrition = recipe.nutrition if hasattr(recipe, 'nutrition') else None
    return render(request, 'users/recipe.html', {'recipe': recipe, 'nutrition': nutrition, 'time': time})

@login_required
def change_options(request):
    return render(request, 'users/change_options.html')