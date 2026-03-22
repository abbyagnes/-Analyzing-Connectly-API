from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination

from .models import Post, UserProfile
from .serializers import PostSerializer
from .factories import PostFactory
from .singleton import LoggerSingleton

import json

# --- 1. AUTHENTICATION & PAGES ---

def hello_world(request):
    return JsonResponse({"message": "Hello, Connectly API!"})

def login_page(request):
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

@csrf_exempt
@require_http_methods(["POST"])
def custom_register(request):
    try:
        data = json.loads(request.body)
        user = User.objects.create_user(
            username=data.get("email"), 
            email=data.get("email"), 
            password=data.get("password1")
        )
        # Default role is 'User' via the model
        UserProfile.objects.get_or_create(user=user)
        token, _ = Token.objects.get_or_create(user=user)
        return JsonResponse({"key": token.key}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def custom_login(request):
    return JsonResponse({"message": "Login successful"})

# --- 2. GOOGLE OAUTH SHELLS ---
def google_oauth_login(request): return JsonResponse({"m": "Google Login"})
def google_oauth_callback(request): return redirect('/dashboard/')
def google_oauth_exchange(request): return JsonResponse({"m": "Exchange"})

# --- 3. INTERACTIVE FEATURE SHELLS ---
@api_view(['POST'])
def like_post(request, id): return JsonResponse({"m": "Liked"})
@csrf_exempt
def comment_post(request, id): return JsonResponse({"m": "Commented"})
def get_comments(request, id): return JsonResponse({"comments": []})

# --- 4. DASHBOARD API ---
@api_view(['GET'])
def dashboard_stats(request): return JsonResponse({'posts_count': 0})
@api_view(['GET'])
def recent_activity(request): return JsonResponse({'activities': []})
@api_view(['GET'])
def news_feed(request): return JsonResponse({'posts': []})

# --- 5. TERMINAL ASSESSMENT: ADVANCED FEATURES ---

class IsAdminUserRole(permissions.BasePermission):
    """TA Requirement: Role-Based Access Control (RBAC)"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'userprofile') and 
            request.user.userprofile.role == 'Admin'
        )

# NEW: This class handles the "Data Management" requirement
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5  
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostListCreateView(generics.ListCreateAPIView):
    """TA Requirement: Caching, Pagination, and Advanced Privacy"""
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny] 
    
    # NEW: Link the pagination class here
    pagination_class = StandardResultsSetPagination 

    def get_queryset(self):
        """Logic: Show public posts OR posts owned by the user"""
        user = self.request.user
        if user.is_authenticated:
            return Post.objects.filter(Q(is_private=False) | Q(user=user)).order_by('-created_at')
        return Post.objects.filter(is_private=False).order_by('-created_at')

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        if not user or user.is_anonymous:
            user = User.objects.first()
        
        content = serializer.validated_data.get('content')
        
        # NEW: Capture if the user clicked "is_private" in Postman
        is_private = serializer.validated_data.get('is_private', False)
        
        # Milestone 1 Integration: Factory Pattern
        # We are now passing 'is_private' to the factory!
        PostFactory.create_post(user, content, is_private)
        
        # Milestone 1 Integration: Singleton Logging
        LoggerSingleton().log(f"TA LOG: {user.username} created a post.")

class AdminOnlyPostDeleteView(generics.DestroyAPIView):
    """TA Requirement: RBAC implementation (Admin only)"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAdminUserRole]