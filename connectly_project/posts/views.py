from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from allauth.account.models import EmailAddress
from .models import Post, Like, Comment, UserProfile
from .serializers import UserSerializer
import json
import requests
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta


def hello_world(request):
    return JsonResponse({"message": "Hello, Connectly API!"})

def login_page(request):
    """Serve the user login page"""
    return render(request, 'login.html')


@csrf_exempt
@require_http_methods(["POST"])
def custom_register(request):
    """Custom registration endpoint that returns user details with token"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")

    # Validation
    if not email or not password1 or not password2:
        return JsonResponse({"error": "Email and passwords are required"}, status=400)

    if password1 != password2:
        return JsonResponse({"error": "Passwords do not match"}, status=400)

    if len(password1) < 8:
        return JsonResponse({"error": "Password must be at least 8 characters"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"error": "Email already registered"}, status=400)

    # Create user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password1
    )

    # Create EmailAddress record for allauth
    EmailAddress.objects.create(
        user=user,
        email=email,
        verified=True,
        primary=True
    )

    # Create or get user profile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get or create token
    token, created = Token.objects.get_or_create(user=user)

    return JsonResponse({
        "key": token.key,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def custom_login(request):
    """Custom login endpoint that returns user details with token"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"error": "Email and password are required"}, status=400)

    # Get user by email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"error": "Invalid email or password"}, status=401)

    # Check password
    if not user.check_password(password):
        return JsonResponse({"error": "Invalid email or password"}, status=401)

    # Get or create token
    token, created = Token.objects.get_or_create(user=user)

    return JsonResponse({
        "key": token.key,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, id):
    """Toggle like/unlike for a post"""
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    user = request.user

    # Check if user already liked the post
    existing_like = Like.objects.filter(user=user, post=post).first()
    
    if existing_like:
        # Unlike the post
        existing_like.delete()
        likes_count = Like.objects.filter(post=post).count()
        return JsonResponse({
            "message": "Post unliked successfully",
            "liked": False,
            "likes_count": likes_count
        })
    else:
        # Like the post
        Like.objects.create(user=user, post=post)
        likes_count = Like.objects.filter(post=post).count()
        return JsonResponse({
            "message": "Post liked successfully",
            "liked": True,
            "likes_count": likes_count
        })


@csrf_exempt
def comment_post(request, id):
    if request.method == "POST":
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)

        user = User.objects.first()

        if not user:
            return JsonResponse({"error": "No user found in database"}, status=400)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        content = data.get("content")

        if not content:
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)

        comment = Comment.objects.create(
            user=user,
            post=post,
            content=content
        )

        return JsonResponse({
            "message": "Comment added",
            "comment": comment.content
        })


def get_comments(request, id):
    try:
        post = Post.objects.get(id=id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found"}, status=404)

    comments = Comment.objects.filter(post=post)

    data = []

    for comment in comments:
        data.append({
            "user": comment.user.username,
            "content": comment.content,
            "created_at": comment.created_at
        })

    return JsonResponse({"comments": data})
@csrf_exempt
@require_http_methods(["POST"])
def google_oauth_login(request):
    """Google OAuth login endpoint that verifies ID token and returns user details with token"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    id_token = data.get("id_token")
    
    if not id_token:
        return JsonResponse({"error": "ID token is required"}, status=400)

    # Verify the ID token with Google
    try:
        # Google's token verification endpoint
        response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        )
        
        if response.status_code != 200:
            return JsonResponse({"error": "Invalid token"}, status=401)
            
        token_info = response.json()
        
        # Verify the token is intended for your app
        expected_client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        if token_info.get('aud') != expected_client_id:
            return JsonResponse({"error": "Token audience mismatch"}, status=401)
            
        # Extract user information
        email = token_info.get('email')
        name = token_info.get('name', '')
        first_name = token_info.get('given_name', '')
        last_name = token_info.get('family_name', '')
        
        if not email:
            return JsonResponse({"error": "Email not found in token"}, status=400)
            
        # Get or create user
        username = email.split('@')[0] if '@' in email else email  # Use email prefix as username
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # If user already exists, update name if it's changed
        if not created:
            # Always update first_name and last_name from Google
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            # Also update username if it's still the full email
            if '@' in user.username:
                user.username = username
            user.save()
            print(f"Updated existing user: {user.email}, first_name: {user.first_name}, username: {user.username}")
        
        # Create EmailAddress record for allauth
        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={
                'verified': True,
                'primary': True
            }
        )
        
        # Create or get user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Get or create DRF token
        token, _ = Token.objects.get_or_create(user=user)
        
        return JsonResponse({
            "key": token.key,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "name": name
            }
        })
        
    except requests.RequestException:
        return JsonResponse({"error": "Failed to verify token with Google"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Authentication failed: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def google_oauth_exchange(request):
    """Exchange authorization code for ID token"""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    auth_code = data.get("code")
    
    if not auth_code:
        return JsonResponse({"error": "Authorization code is required"}, status=400)

    # Exchange authorization code for tokens
    try:
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
                'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
                'code': auth_code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://127.0.0.1:8000/auth/google/callback/'
            }
        )
        
        if token_response.status_code != 200:
            return JsonResponse({"error": "Failed to exchange authorization code"}, status=400)
            
        token_data = token_response.json()
        
        # Get user info with the access token
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {token_data.get("access_token")}'}
        )
        
        if user_response.status_code != 200:
            return JsonResponse({"error": "Failed to get user info"}, status=400)
            
        user_info = user_response.json()
        
        # Get ID token if available
        id_token = token_data.get('id_token')
        
        if not id_token:
            return JsonResponse({"error": "No ID token received"}, status=400)
        
        return JsonResponse({"id_token": id_token})
        
    except requests.RequestException:
        return JsonResponse({"error": "Failed to exchange code with Google"}, status=500)
    except Exception as e:
        return JsonResponse({"error": f"Token exchange failed: {str(e)}"}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def google_oauth_callback(request):
    """Google OAuth callback endpoint that handles authorization code"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        return JsonResponse({"error": f"OAuth error: {error}"}, status=400)
    
    if not code:
        return JsonResponse({"error": "Authorization code not provided"}, status=400)
    
    # Exchange authorization code for tokens
    try:
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id'],
                'client_secret': settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret'],
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'http://127.0.0.1:8000/auth/google/callback/'
            },
            verify=False  # Bypass SSL verification for development
        )
        
        if token_response.status_code != 200:
            return JsonResponse({"error": "Failed to exchange authorization code"}, status=400)
            
        token_data = token_response.json()
        
        # Get user info with the access token
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {token_data.get("access_token")}'}
        )
        
        if user_response.status_code != 200:
            return JsonResponse({"error": "Failed to get user info"}, status=400)
            
        user_info = user_response.json()
        
        # Get ID token if available
        id_token = token_data.get('id_token')
        
        if not id_token:
            return JsonResponse({"error": "No ID token received"}, status=400)
        
        # Create or get user and DRF token
        email = user_info.get('email')
        name = user_info.get('name', '')
        first_name = user_info.get('given_name', '')
        last_name = user_info.get('family_name', '')
        
        username = email.split('@')[0] if '@' in email else email  # Use email prefix as username
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        
        # If user already exists, update their information
        if not created:
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if '@' in user.username:
                user.username = username
            user.save()
            print(f"Updated existing user in callback: {user.email}, first_name: {user.first_name}")
        
        # Create EmailAddress record for allauth
        email_address, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={
                'verified': True,
                'primary': True
            }
        )
        
        # Create or get user profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # Get or create DRF token
        token, _ = Token.objects.get_or_create(user=user)
        
        # Prepare auth data for frontend
        auth_data = {
            "token": token.key,
            "user": {
                "id": user.id,
                "email": email,
                "username": user.username,
                "first_name": first_name,
                "last_name": last_name,
                "name": name
            }
        }
        
        # URL encode the auth data
        import urllib.parse
        encoded_auth = urllib.parse.quote(json.dumps(auth_data))
        
        # Redirect to login page with google_auth parameter
        return redirect(f'http://127.0.0.1:8000/login/?google_auth={encoded_auth}')
        
    except Exception as e:
        return JsonResponse({"error": f"Authentication failed: {str(e)}"}, status=500)


def dashboard_view(request):
    """Serve the dashboard page"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('/login/')
    return render(request, 'dashboard.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the authenticated user"""
    try:
        user = request.user
        
        # Get user's posts count
        posts_count = Post.objects.filter(user=user).count()
        
        # Get likes received on user's posts
        likes_count = Like.objects.filter(post__user=user).count()
        
        # Get comments made by user
        comments_count = Comment.objects.filter(user=user).count()
        
        # Calculate activity score (posts + likes + comments)
        activity_score = posts_count + likes_count + comments_count
        
        return JsonResponse({
            'posts_count': posts_count,
            'likes_count': likes_count,
            'comments_count': comments_count,
            'activity_score': activity_score
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activity(request):
    """Get recent activity for the authenticated user"""
    try:
        user = request.user
        
        # Get recent posts
        recent_posts = Post.objects.filter(user=user).order_by('-created_at')[:5]
        activities = []
        
        for post in recent_posts:
            activities.append({
                'type': 'post',
                'title': f'Created a new post: "{post.content[:50]}..."',
                'time': get_time_ago(post.created_at),
                'icon': '📝'
            })
        
        # Get recent likes
        recent_likes = Like.objects.filter(user=user).select_related('post').order_by('-created_at')[:3]
        for like in recent_likes:
            activities.append({
                'type': 'like',
                'title': f'Liked a post: "{like.post.content[:50]}..."',
                'time': get_time_ago(like.created_at),
                'icon': '❤️'
            })
        
        # Get recent comments
        recent_comments = Comment.objects.filter(user=user).select_related('post').order_by('-created_at')[:3]
        for comment in recent_comments:
            activities.append({
                'type': 'comment',
                'title': f'Commented on: "{comment.post.content[:50]}..."',
                'time': get_time_ago(comment.created_at),
                'icon': '💬'
            })
        
        # Sort all activities by time (most recent first)
        activities.sort(key=lambda x: x['time'], reverse=True)
        
        # Return only the 10 most recent activities
        return JsonResponse({'activities': activities[:10]})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def news_feed(request):
    """Get news feed for the authenticated user with pagination"""
    try:
        user = request.user
        
        # Get pagination parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        # Get sorting parameter (default: newest first)
        sort_by = request.GET.get('sort', 'newest')
        
        # Get filter parameter (default: all posts)
        filter_by = request.GET.get('filter', 'all')
        
        # Start with all posts
        posts = Post.objects.select_related('user').prefetch_related('like_set', 'comment_set')
        
        # Apply user-specific filters
        if filter_by == 'following':
            # TODO: Add following logic when you implement user following
            posts = posts.filter(user=user)  # For now, just show user's posts
        elif filter_by == 'my_posts':
            posts = posts.filter(user=user)
        # 'all' shows all posts (default)
        
        # Apply sorting
        if sort_by == 'newest':
            posts = posts.order_by('-created_at')
        elif sort_by == 'oldest':
            posts = posts.order_by('created_at')
        elif sort_by == 'most_liked':
            posts = posts.annotate(like_count=Count('like')).order_by('-like_count', '-created_at')
        elif sort_by == 'most_commented':
            posts = posts.annotate(comment_count=Count('comment')).order_by('-comment_count', '-created_at')
        else:
            posts = posts.order_by('-created_at')  # Default to newest
        
        # Calculate pagination
        total_posts = posts.count()
        total_pages = (total_posts + page_size - 1) // page_size
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        # Get paginated posts
        paginated_posts = posts[start_index:end_index]
        
        # Format posts for response
        posts_data = []
        for post in paginated_posts:
            posts_data.append({
                'id': post.id,
                'content': post.content,
                'author': {
                    'id': post.user.id,
                    'username': post.user.username,
                    'first_name': post.user.first_name,
                    'last_name': post.user.last_name,
                    'email': post.user.email
                },
                'created_at': post.created_at.isoformat(),
                'likes_count': post.like_set.count(),
                'comments_count': post.comment_set.count(),
                'is_liked_by_user': post.like_set.filter(user=user).exists(),
                'is_author': post.user == user
            })
        
        return JsonResponse({
            'posts': posts_data,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_posts': total_posts,
                'page_size': page_size,
                'has_next': page < total_pages,
                'has_previous': page > 1
            },
            'filters': {
                'sort': sort_by,
                'filter': filter_by
            }
        })
        
    except ValueError as e:
        return JsonResponse({'error': f'Invalid parameter: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_time_ago(created_at):
    """Helper function to get human-readable time ago string"""
    now = timezone.now()
    diff = now - created_at
    
    if diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        if minutes == 0:
            return "Just now"
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days} day{'s' if days != 1 else ''} ago"
    else:
        weeks = int(diff.days / 7)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
