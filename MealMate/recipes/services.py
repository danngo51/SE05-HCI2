import openai
from .models import Embedded_Recipe

def generate_embedding(input_text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=input_text
    )
    return response['data'][0]['embedding']

def filter_recipes_by_preferences(user_profile, excluded_recipe_ids):
    profile_embedding = user_profile.embedding
    recipes = Embedded_Recipe.objects.filter(
        embedding__distance_lte=(profile_embedding, 0.7)
    ).exclude(id__in=excluded_recipe_ids).order_by("?")[:10]

    return recipes