from django.core.management.base import BaseCommand
from users.models import UserProfile
from users.services import generate_user_profile_embedding
from django.db import transaction
from numpy import ndarray

class Command(BaseCommand):
    help = "Generate embeddings for all user preferences and store them in the UserProfile model"

    def handle(self, *args, **kwargs):
        user_profiles = UserProfile.objects.all()
        total = user_profiles.count()
        count = 0

        self.stdout.write(f"Starting to process {total} user profiles...")

        for profile in user_profiles.iterator():
            # Ensure embedding field is either None or check its length
            if profile.embedding is not None and isinstance(profile.embedding, ndarray) and profile.embedding.size > 0:
                self.stdout.write(f"Skipping user {profile.user.username}: Embedding already exists.")
                continue

            try:
                # Wrap embedding generation in a transaction
                with transaction.atomic():
                    generate_user_profile_embedding(profile.user)
                    count += 1
                    self.stdout.write(f"Embedded user preferences for: {profile.user.username}")

            except Exception as e:
                self.stderr.write(f"Failed to process user {profile.user.username}: {str(e)}")

        self.stdout.write(f"Successfully processed {count} user profiles out of {total}")
