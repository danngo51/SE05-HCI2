import psycopg2
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor
import time
import signal
import sys

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


# Database connection
connection = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    port=os.getenv("DB_PORT"),
)
cursor = connection.cursor()



# Configurable parameters
THREAD_COUNT = 6      # Number of threads for parallel processing
BATCH_SIZE = 200      # Number of recipes per batch
MAX_RECIPES = None    # Max number of recipes to process (set to None for all)


def fetch_recipes_by_key(batch_size, last_id):
    """
    Fetch a batch of recipes using primary key-based pagination.
    """
    query = """
        SELECT
            r.id AS recipe_id,
            r.title,
            r.description,
            r.instructions,
            n.calories,
            n.total_fat,
            n.sugar,
            n.sodium,
            n.protein,
            n.saturated_fat,
            n.carbohydrates,
            ARRAY_AGG(DISTINCT i.name) AS ingredients,
            ARRAY_AGG(DISTINCT t.name) AS tags
        FROM
            recipes_recipe r
        LEFT JOIN
            recipes_nutrition n ON r.id = n.recipe_id
        LEFT JOIN
            recipes_recipe_ingredients ri ON r.id = ri.recipe_id
        LEFT JOIN
            recipes_ingredient i ON ri.ingredient_id = i.id
        LEFT JOIN
            recipes_recipe_tags rt ON r.id = rt.recipe_id
        LEFT JOIN
            recipes_tag t ON rt.tag_id = t.id
        WHERE
            r.id > %s
            AND NOT EXISTS (
                SELECT 1
                FROM recipes_embedded_recipe e
                WHERE e.recipe_id = r.id
            )
        GROUP BY
            r.id, n.calories, n.total_fat, n.sugar, n.sodium, n.protein, n.saturated_fat, n.carbohydrates
        LIMIT %s;
    """
    cursor.execute(query, (last_id, batch_size))
    return cursor.fetchall()


def preprocess_recipe(recipe):
    """
    Prepare recipe as a single text string for embedding.
    """
    nutrition = (
        f"Calories: {recipe[4]}, Total Fat: {recipe[5]}, "
        f"Sugar: {recipe[6]}, Sodium: {recipe[7]}, "
        f"Protein: {recipe[8]}, Saturated Fat: {recipe[9]}, "
        f"Carbohydrates: {recipe[10]}"
        if recipe[4] is not None else ""
    )
    return (
        f"{recipe[1]} "  # title
        f"{recipe[2]} "  # description
        f"{nutrition} "
        f"{', '.join(recipe[11])} "  # ingredients
        f"{', '.join(recipe[12])} "  # tags
        f"Instructions: {' '.join(recipe[3])}"  # instructions
    )


def save_embeddings(recipe_ids, embeddings):
    """
    Save recipe embeddings to the database.
    """
    query = "INSERT INTO recipes_embedded_recipe (recipe_id, embedding) VALUES (%s, %s)"
    for recipe_id, embedding in zip(recipe_ids, embeddings):
        cursor.execute(query, (recipe_id, embedding))
    connection.commit()


def embed_recipes_with_retry(batch_size, last_id, retries=3):
    """
    Embed recipes in a single batch with retry logic and skip problematic ones after retries.
    """
    skipped_recipes = []  # List to store skipped recipe IDs

    for attempt in range(retries):
        try:
            recipes = fetch_recipes_by_key(batch_size, last_id)
            if not recipes:
                print(f"No recipes found after ID {last_id}.")
                return 0, last_id, skipped_recipes

            recipe_ids = [recipe[0] for recipe in recipes]
            inputs = []
            for recipe in recipes:
                try:
                    inputs.append(preprocess_recipe(recipe))
                except Exception as e:
                    # Log and skip invalid recipes during preprocessing
                    print(f"Skipping recipe ID {recipe[0]} during preprocessing. Error: {e}")
                    skipped_recipes.append(recipe[0])
                    continue

            if not inputs:
                # If no valid inputs, return and log skipped recipes
                print(f"All recipes in batch starting from ID {last_id} were skipped.")
                return 0, last_id, skipped_recipes

            print(f"Processing batch starting from ID {last_id}...")

            # Call OpenAI API
            response = client.embeddings.create(
                input=inputs,
                model="text-embedding-3-small"
            )
            embeddings = [item.embedding for item in response.data]

            # Save embeddings to the database
            valid_recipe_ids = [id for id in recipe_ids if id not in skipped_recipes]
            save_embeddings(valid_recipe_ids, embeddings)

            print(f"Batch starting from ID {last_id} completed.")
            return len(valid_recipe_ids), recipe_ids[-1], skipped_recipes

        except Exception as e:
            print(f"Attempt {attempt + 1} failed for ID {last_id}. Error: {e}")
            if attempt == retries - 1:
                print(f"Skipping batch starting from ID {last_id} after {retries} retries.")
                skipped_recipes.extend([r[0] for r in recipes])  # Log skipped recipes
                return 0, last_id, skipped_recipes

    return 0, last_id, skipped_recipes


def worker(thread_index, total_recipes):
    processed = 0
    last_id = last_ids[thread_index]
    thread_skipped = []  # Skipped recipes for this thread

    while processed < total_recipes // THREAD_COUNT:
        count, last_id, skipped = embed_recipes_with_retry(BATCH_SIZE, last_id)
        processed += count
        thread_skipped.extend(skipped)
        if count == 0:
            break

    return processed, thread_skipped



def parallel_embedding(thread_count, batch_size, max_recipes):
    """
    Run embedding process in parallel using primary key-based pagination.
    """
    start_time = time.time()
    start = time.asctime()
    print(f"Start time: {start}")

    cursor.execute("SELECT COUNT(*) FROM recipes_recipe")
    total_recipes = cursor.fetchone()[0]
    if max_recipes:
        total_recipes = min(total_recipes, max_recipes)

    global last_ids
    last_ids = [0] * thread_count
    all_skipped = []  # Collect skipped recipes across all threads

    def worker_wrapper(thread_index):
        return worker(thread_index, total_recipes)

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        results = list(executor.map(worker_wrapper, range(thread_count)))

    total_processed = sum(res[0] for res in results)  # Sum 'processed' counts
    for res in results:
        all_skipped.extend(res[1])  # Collect skipped recipes from all threads

    end_time = time.time()
    end = time.asctime()
    print(f"Embedding process completed. {total_processed} recipes processed in {end_time - start_time:.2f} seconds.")
    print(f"Skipped recipes: {all_skipped}")
    print(f"Start time: {start}, End time: {end}")

    # Optionally, save skipped recipe IDs to a file
    with open("skipped_recipes.log", "w") as log_file:
        for recipe_id in all_skipped:
            log_file.write(f"{recipe_id}\n")



def signal_handler(sig, frame):
    """
    Gracefully handle interrupts.
    """
    print("Interrupted! Closing database connection...")
    cursor.close()
    connection.close()
    sys.exit(0)


# Attach signal handler
signal.signal(signal.SIGINT, signal_handler)

# Run the embedding process
try:
    parallel_embedding(THREAD_COUNT, BATCH_SIZE, MAX_RECIPES)
finally:
    cursor.close()
    connection.close()
