import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI

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


# Personalized Recommendations:
#Fetch recipes most similar to a user’s preferences.
def recommend_recipes_by_user(user_profile, threshold=0.7, limit=10):
    """
    Recommend recipes based on similarity to the user's profile embedding.

    Arguments:
        user_profile (UserProfile): The user's profile with preferences and embedding.
        threshold (float): The similarity threshold.
        limit (int): The number of recipes to return.

    Returns:
        QuerySet: Recommended recipes.
    """
    if not user_profile.embedding:
        return Recipe.objects.order_by("?")[:20]
        raise ValueError("User profile does not have an embedding.")

    # Query recipes most similar to the user's embedding
    recommended_recipes = Embedded_Recipe.objects.filter(
        embedding__distance_lte=(user_profile.embedding, threshold)
    ).order_by("embedding__distance")[:limit]

    return recommended_recipes



#Search-Based Recommendations:
#Combine search query embeddings with user preferences for enhanced recommendations.
def search_recipes(query, threshold=0.7, limit=10):
    """
    Search for recipes based on similarity to a query embedding.

    Args:
        query (str): The search query.
        threshold (float): The similarity threshold.
        limit (int): The number of recipes to return.

    Returns:
        QuerySet: Recipes matching the search query.
    """
    # Generate an embedding for the search query
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=query
    )
    query_embedding = response['data'][0]['embedding']

    # Query recipes most similar to the query embedding
    matching_recipes = Embedded_Recipe.objects.filter(
        embedding__distance_lte=(query_embedding, threshold)
    ).order_by("embedding__distance")[:limit]

    return matching_recipes

#Allergy Filtering:
#Exclude recipes containing ingredients similar to allergens.
def filter_recipes_by_allergies(allergens, recipe_queryset, threshold=0.7):
    """
    Exclude recipes containing ingredients similar to the given allergens.

    Args:
        allergens (list): List of allergen names (e.g., ["peanut", "walnut"]).
        recipe_queryset (QuerySet): Recipes to filter.
        threshold (float): The similarity threshold.

    Returns:
        QuerySet: Filtered recipes.
    """
    excluded_ingredients = []

    for allergen in allergens:
        # Generate an embedding for the allergen
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=allergen
        )
        allergen_embedding = response['data'][0]['embedding']

        # Find ingredients similar to the allergen
        similar_ingredients = Embedded_Ingredient.objects.filter(
            embedding__distance_lte=(allergen_embedding, threshold)
        ).values_list("ingredient_id", flat=True)

        excluded_ingredients.extend(similar_ingredients)

    # Exclude recipes containing these ingredients
    return recipe_queryset.exclude(ingredients__id__in=excluded_ingredients)