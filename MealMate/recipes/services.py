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

from recipes.models import Ingredient, Embedded_Ingredient, Recipe, Embedded_Recipe, Embedded_Recipe, Embedded_Ingredient



