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


def generate_user_profile_embedding(request):
    """
    Generate embeddings for a user's profile preferences and health concerns, and store them in the `UserProfile` model.
    """
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Generate user profile embedding
        preferences_text = (
            f"Cuisines: {profile.preferred_cuisines} "
            f"Diet: {profile.diet} "
            f"Health Concerns: {profile.health_concerns} "
            f"Budget: {profile.budget.min_value}-{profile.budget.max_value if profile.budget else 'No Budget'}"
        )
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=preferences_text
        )
        profile_embedding = response.data[0].embedding
        profile.embedding = profile_embedding

        # Generate health concern embedding if health concerns exist
        if profile.health_concerns:
            health_concerns_text = " ".join(profile.health_concerns)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=health_concerns_text
            )
            health_concern_embedding = response.data[0].embedding
            profile.health_concern_embedding = health_concern_embedding

        # Save the updated profile
        profile.save()

    except Exception as e:
        # Log the error and handle gracefully
        print(f"Error generating embeddings for user profile: {str(e)}")
        raise


def generate_user_profile_embedding(user):
    """
    Generate embeddings for a user's profile preferences and health concerns, and store them in the `UserProfile` model.

    Args:
        user (User): The user instance for whom to generate the embeddings.
    """
    profile = UserProfile.objects.get(user=user)

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
        health_concerns_text = " ".join(profile.health_concerns)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=health_concerns_text
        )
        health_concern_embedding = response.data[0].embedding
        profile.health_concern_embedding = health_concern_embedding

    # Save the updated profile
    profile.save()

