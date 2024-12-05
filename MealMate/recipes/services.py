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

from recipes.models import Ingredient, Embedded_Ingredient, Embedded_Recipe, Embedded_Recipe, Embedded_Ingredient


def generate_recipe_embedding(recipe):
    """
    Generate an embedding for a single recipe and save it in the Embedded_Recipe model.

    Args:
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
