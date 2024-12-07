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

from users.models import UserProfile

def generate_user_profile_embedding(user):
    """
    Generate embeddings for a user's profile preferences and health concerns, and store them in the `UserProfile` model.

    Args:
        user (User): The user instance for whom to generate the embeddings.
    """
    profile = UserProfile.objects.get(user=user)

    profile.embedding = None
    profile.health_concern_embedding = None
    profile.save()

    # Generate user profile embedding
    budget_text = (
        f"{profile.budget.min_value}-{profile.budget.max_value}"
        if profile.budget else "No Budget"
    )
    preferences_text = (
        f"Cuisines: {profile.preferred_cuisines} "
        f"Diet: {profile.diet} "
        f"Health Concerns: {profile.health_concerns} "
        f"Budget: {budget_text}"
    )
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=preferences_text
    )
    profile_embedding = response.data[0].embedding
    profile.embedding = profile_embedding

    # Generate health concern embedding if health concerns exist
    if profile.health_concerns:
        print("Health concerns updated")
        health_concerns_text = " ".join(profile.health_concerns)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=health_concerns_text
        )
        health_concern_embedding = response.data[0].embedding
        profile.health_concern_embedding = health_concern_embedding

    # Save the updated profile
    print("user embedding updated")
    profile.save()


from recipes.models import Recipe, RecipeRating
from django.db.models import Avg, Count

def handle_rating(user, recipe_id, rating_value=None):
    """
    Handles creating, updating, or retrieving a rating.

    Args:
        user (User): The user submitting the rating.
        recipe_id (int): The ID of the recipe being rated.
        rating_value (int, optional): The rating value to submit. If None, retrieves the rating.

    Returns:
        dict: {
            'success': bool,
            'message': str,
            'rating': RecipeRating or None,
            'average_rating': float or None,
            'rating_count': int,
        }
    """
    try:
        recipe = Recipe.objects.get(id=recipe_id)

        if rating_value is not None:
            # Create or update the rating
            rating, created = RecipeRating.objects.update_or_create(
                user=user,
                recipe=recipe,
                defaults={'rating': rating_value}
            )
            # Calculate average rating and count of ratings
            stats = RecipeRating.objects.filter(recipe=recipe).aggregate(
                avg_rating=Avg('rating'),
                rating_count=Count('id')
            )
            return {
                'success': True,
                'message': "Rating submitted successfully!" if created else "Rating updated successfully!",
                'rating': rating,
                'average_rating': stats['avg_rating'],
                'rating_count': stats['rating_count'],
            }

        # Retrieve existing rating
        rating = RecipeRating.objects.filter(user=user, recipe=recipe).first()
        stats = RecipeRating.objects.filter(recipe=recipe).aggregate(
            avg_rating=Avg('rating'),
            rating_count=Count('id')
        )
        return {
            'success': True,
            'message': "Rating retrieved successfully.",
            'rating': rating,
            'average_rating': stats['avg_rating'],
            'rating_count': stats['rating_count'],
        }

    except Recipe.DoesNotExist:
        return {
            'success': False,
            'message': "Recipe not found.",
            'rating': None,
            'average_rating': None,
            'rating_count': None,
        }


