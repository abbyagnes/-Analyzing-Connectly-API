#!/usr/bin/env python
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly_project.settings')
django.setup()

from posts.models import Post
from django.contrib.auth.models import User

# Get or create a test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
)

# Create sample posts
Post.objects.get_or_create(
    user=user,
    content='Welcome to Connectly! This is our first sample post. 🎉',
    defaults={}
)

Post.objects.get_or_create(
    user=user,
    content='Just discovered this amazing platform! The user interface is so clean and intuitive. 💻',
    defaults={}
)

Post.objects.get_or_create(
    user=user,
    content='Working on some exciting new features. Stay tuned for updates! 🚀',
    defaults={}
)

print(f'Created sample posts for user: {user.username}')
print(f'Total posts: {Post.objects.count()}')
