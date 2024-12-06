import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from pgvector.django import L2Distance, CosineDistance
import random

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the directory of the current script (main.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the full path to the .env file
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

API_KEY = os.getenv("API_KEY")

client = OpenAI(api_key=API_KEY,)

from recipes.models import Ingredient, Embedded_Ingredient, Recipe, Embedded_Recipe, Embedded_Recipe, Embedded_Ingredient
from django.db.models import Case, When


def generate_recipe_embedding(recipe):
    """
    Generate an embedding for a single recipe and save it in the Embedded_Recipe model.

    Arguments:
        recipe (Recipe): The recipe instance to generate an embedding for.
    """
    input_text = (
        f"{recipe.title} "
        f"{recipe.description} "
        f"{', '.join([ingredient.name for ingredient in recipe.ingredients.all()])} "
        f"{', '.join([tag.name for tag in recipe.tags.all()])} "
        f"Instructions: {' '.join(recipe.instructions)}"
    )
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=input_text
    )
    embedding = response.data[0].embedding

    # Save the embedding in the Embedded_Recipe model
    Embedded_Recipe.objects.create(recipe=recipe, embedding=embedding)



def generate_ingredient_embeddings():
    """
    Generate embeddings for all ingredients and store them in the Embedded_Ingredient table.
    """
    ingredients = Ingredient.objects.all()
    count = 0

    for ingredient in ingredients:
        # Skip if already embedded
        if Embedded_Ingredient.objects.filter(ingredient=ingredient).exists():
            continue

        try:
            # Generate embedding using OpenAI
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=ingredient.name
            )
            embedding = response.data[0].embedding

            # Save the embedding in the database
            Embedded_Ingredient.objects.create(ingredient=ingredient, embedding=embedding)
            count += 1
            print(f"Embedded ingredient: {ingredient.name}")

        except Exception as e:
            print(f"Failed to embed ingredient {ingredient.name}: {str(e)}")

    print(f"Successfully embedded {count} ingredients")


# Threshold ranges from 0 to 2
    # Higher thresholds increase the chance of finding more relevant results, but may also lead to less accurate recommendations.
    # Lower thresholds decrease the chance of finding more relevant results, but may also lead to more accurate recommendations.


# Personalized Recommendations:
#Fetch recipes most similar to a user’s preferences. Recommended Threshold: 0.3 - 0.7
def recommend_recipes_by_user(user_profile, threshold=0.7, limit=50):
    """
    Recommend recipes based on similarity to the user's profile embedding.

    Args:
        user_profile (UserProfile): The user's profile with preferences and embedding.
        threshold (float): The similarity threshold.
        limit (int): The number of recipes to return.

    Returns:
        QuerySet: Recommended `Recipe` objects.
    """
    if user_profile.embedding is None:
        print('helle')
        raise ValueError("User profile does not have an embedding.")

    # Find recipe IDs based on user preferences
    recipes_with_distances = Embedded_Recipe.objects.annotate(
    distance=CosineDistance("embedding", user_profile.embedding)
    ).filter(
        distance__lte=threshold
    ).order_by("distance")[:limit*3] #.values_list("recipe_id", flat=True)

    # Convert QuerySet to list and calculate weights
    # Higher ratings are more likely to be returned
    # Perform weighted random sampling
    recipe_list = list(recipes_with_distances)
    weights = [1 / (recipe.distance + 1e-6) for recipe in recipe_list]
    sampled_recipes = random.choices(recipe_list, weights=weights, k=limit)

    # Get recipe IDs from the sampled results
    recipe_ids = [r.recipe_id for r in sampled_recipes]

    # Preserve the order of `recipe_ids` in the final query
    return Recipe.objects.filter(id__in=recipe_ids).order_by(
        Case(*[When(id=pk, then=pos) for pos, pk in enumerate(recipe_ids)])
    )



#Search-Based Recommendations:
#Combine search query embeddings with user preferences for enhanced recommendations. Recommended Threshold: 0.2 - 0.5
def search_recipes(query, threshold=0.5, limit=50):
    """
    Search for recipes based on similarity to a query embedding.

    Args:
        query (str): The search query.
        threshold (float): The similarity threshold.
        limit (int): The number of recipes to return.

    Returns:
        QuerySet: Recommended `Recipe` objects.
    """
    # Generate an embedding for the search query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding

    # Find recipe IDs based on the query embedding
    recipes_with_distances = Embedded_Recipe.objects.annotate(
    distance=CosineDistance("embedding", query_embedding)
    ).filter(
        distance__lte=threshold
    ).order_by("distance")[:limit*3] #.values_list("recipe_id", flat=True)

    # Convert QuerySet to list and calculate weights
    # Higher ratings are more likely to be returned
    recipe_list = list(recipes_with_distances)
    weights = [1 / (recipe.distance + 1e-6) for recipe in recipe_list]  # Assigning higher weights for closer distances

    # Perform weighted random sampling
    sampled_recipes = random.choices(recipe_list, weights=weights, k=limit)

    # Fetch full Recipe objects
    recipe_ids = [r.recipe_id for r in sampled_recipes]
    return Recipe.objects.filter(id__in=recipe_ids)


#Heath Concerns:
#Exclude recipes containing ingredients related to Health Concerns. Recommended Threshold: 0.1 - 0.3
def filter_recipes_by_health_concerns(user_profile, recipe_queryset, threshold=0.3):
    """
    Exclude recipes containing ingredients conflicting with the user's health concerns.

    Args:
        user_profile (UserProfile): The user's profile with precomputed health concern embedding.
        recipe_queryset (QuerySet): Recipes to filter.
        threshold (float): The similarity threshold.

    Returns:
        QuerySet: Filtered `Recipe` objects.
    """
    if user_profile.health_concern_embedding is None:
        return recipe_queryset

    # Find ingredients similar to the user's health concerns
    similar_ingredients = Embedded_Ingredient.objects.annotate(
        distance=CosineDistance("embedding", user_profile.health_concern_embedding)
    ).filter(
        distance__lte=threshold
    ).values_list("ingredient_id", flat=True)

    # Exclude recipes containing these conflicting ingredients
    return recipe_queryset.exclude(ingredients__id__in=similar_ingredients)



def get_personalized_recommendations_with_health_concerns(
    user_profile, query=None, threshold_user_pref=0.7, threshold_search=0.5, threshold_filter=0.3, limit=50):
    """
    Fetch personalized recipe recommendations by generating more recipes initially.
    """
    initial_limit = limit*2  # Generate more recipes to ensure enough after filtering

    # Step 1: Get user-preference-based recommendations
    recipes = recommend_recipes_by_user(user_profile, threshold_user_pref, initial_limit)

    # Step 2: If a search query is provided, refine results
    if query:
        search_results = search_recipes(query, threshold_search, initial_limit)
        recipes = recipes & search_results  # Intersection of both QuerySets

    # Step 3: Apply health concern filtering
    recipes = filter_recipes_by_health_concerns(user_profile, recipes, threshold_filter)

    # Step 4: Limit the final results
    return recipes[:limit]
