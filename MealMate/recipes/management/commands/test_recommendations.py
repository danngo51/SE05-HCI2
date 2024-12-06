from django.core.management.base import BaseCommand
from users.models import UserProfile

class Command(BaseCommand):
    help = "Test personalized recommendations with health concerns for a user."

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, required=True, help="ID of the user profile")
        parser.add_argument('--query', type=str, default=None, help="Optional search query")
        parser.add_argument('--threshold_user_pref', type=float, default=0.7, help="Threshold for user preferences")
        parser.add_argument('--threshold_search', type=float, default=0.5, help="Threshold for search query")
        parser.add_argument('--threshold_filter', type=float, default=0.3, help="Threshold for health concern filtering")
        parser.add_argument('--limit', type=int, default=20, help="Number of recipes to return")

    def handle(self, *args, **options):
        # Move import here to avoid circular dependency
        from recipes.services import get_personalized_recommendations_with_health_concerns

        # Extract arguments
        user_id = options['user_id']
        query = options['query']
        threshold_user_pref = options['threshold_user_pref']
        threshold_search = options['threshold_search']
        threshold_filter = options['threshold_filter']
        limit = options['limit']

        try:
            # Fetch the user profile
            user_profile = UserProfile.objects.get(user_id=user_id)

            # Get recommendations
            recommendations = get_personalized_recommendations_with_health_concerns(
                user_profile=user_profile,
                query=query,
                threshold_user_pref=threshold_user_pref,
                threshold_search=threshold_search,
                threshold_filter=threshold_filter,
                limit=limit
            )

            # Output the results
            self.stdout.write(f"\nRecommendations for user {user_profile.user.username}:\n")
            for recipe in recommendations:
                self.stdout.write(f"- {recipe.title} ({recipe.minutes} minutes)\n")
        except UserProfile.DoesNotExist:
            self.stderr.write(f"UserProfile with user_id {user_id} does not exist.")
        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")
