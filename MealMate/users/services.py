import os
from dotenv import load_dotenv
from pathlib import Path
import openai

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Get the directory of the current script (main.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Construct the full path to the .env file
dotenv_path = os.path.join(basedir, '.env')
load_dotenv(dotenv_path=dotenv_path)
load_dotenv()

API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY

from users.models import UserProfile

def generate_user_profile_embedding(request):
    """
    Generate an embedding for a user's profile preferences and store it in the `UserProfile` model.
    """
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        preferences_text = (
            f"Cuisines: {profile.preferred_cuisines} "
            f"Diet: {profile.diet} "
            f"Health Concerns: {profile.health_concerns} "
            f"Budget: {profile.budget.min_value}-{profile.budget.max_value}"
        )
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=preferences_text
        )
        embedding = response['data'][0]['embedding']
        profile.embedding = embedding
        profile.save()
    except Exception as e:
        # Log the error and handle gracefully
        print(f"Error generating user profile embedding: {str(e)}")
        raise

