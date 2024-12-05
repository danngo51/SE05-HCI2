from django.core.management.base import BaseCommand
from recipes.models import Recipe, Embedded_Recipe
from recipes.services import generate_recipe_embedding
from django.db import transaction

class Command(BaseCommand):
    help = "Generate embeddings for all recipes and store them in the Embedded_Recipe table"

    def handle(self, *args, **options):
        """
        Process all recipes in batches, generating embeddings and storing them.
        """
        batch_size = 500  # Number of recipes to process at a time
        recipes = Recipe.objects.all()
        total = recipes.count()
        count = 0

        self.stdout.write(self.style.SUCCESS(f"Starting to process {total} recipes..."))

        for recipe in recipes.iterator(chunk_size=batch_size):
            # Skip if already embedded
            if Embedded_Recipe.objects.filter(recipe=recipe).exists():
                continue

            try:
                # Wrap each embedding in a transaction to ensure atomicity
                with transaction.atomic():
                    generate_recipe_embedding(recipe)
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"Embedded recipe: {recipe.title} , nr.: {count}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to process recipe: {recipe.title}. Error: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully embedded {count} recipes out of {total}"))

