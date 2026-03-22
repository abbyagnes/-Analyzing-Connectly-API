# MILESTONE 1 INTEGRATION: Factory Pattern
# This centralizes post creation logic for consistency and maintainability.
from posts.models import Post

class PostFactory:
    @staticmethod
    def create_post(user, content, is_private=False): # Added is_private here
        return Post.objects.create(
            user=user, 
            content=content, 
            is_private=is_private # Added is_private here
        )