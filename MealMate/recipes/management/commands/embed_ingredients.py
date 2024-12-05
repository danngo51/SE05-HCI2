from django.core.management.base import BaseCommand
from recipes.services import generate_ingredient_embeddings

class Command(BaseCommand):
    help = "Generate embeddings for all ingredients and store them in the Embedded_Ingredient table"

    def handle(self, *args, **kwargs):
        """
        Process all ingredients and generate embeddings.
        """
        self.stdout.write("Starting ingredient embedding...")
        generate_ingredient_embeddings()
        self.stdout.write("Ingredient embedding completed.")
