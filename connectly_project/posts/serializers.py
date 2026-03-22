from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import UserProfile, Post  # Added 'Post' here

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['google_id', 'profile_picture', 'user']

class AuthTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = UserSerializer()
    profile = UserProfileSerializer(required=False, allow_null=True)

# --- ADD THIS FOR THE TERMINAL ASSESSMENT ---

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'created_at', 'is_private']
        # 'is_private' is essential for your TA Privacy requirements!
