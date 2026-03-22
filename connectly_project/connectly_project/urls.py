# --- UPDATE YOUR IMPORTS AT THE TOP ---
from django.contrib import admin
from django.urls import path, include
# Added PostListCreateView to the end of this list
from posts.views import (
    hello_world, like_post, comment_post, get_comments, 
    custom_register, custom_login, google_oauth_login, 
    google_oauth_callback, google_oauth_exchange, login_page, 
    dashboard_view, dashboard_stats, recent_activity, news_feed,
    PostListCreateView 
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', login_page, name='root'),
    path('admin/', admin.site.urls),
    path('hello/', hello_world),
    
    path('login/', login_page, name='login_page'),
    
    path('auth/registration/', custom_register, name='custom_register'),
    path('auth/login/', custom_login, name='custom_login'),
    
    # --- ADD THIS LINE FOR YOUR TERMINAL ASSESSMENT ---
    path('api/posts/', PostListCreateView.as_view(), name='post_list_create'),

    # Existing post endpoints
    path('posts/<int:id>/like/', like_post),
    path('posts/<int:id>/comment/', comment_post),
    path('posts/<int:id>/comments/', get_comments),
    
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('api/dashboard/activity/', recent_activity, name='recent_activity'),
    path('api/feed/', news_feed, name='news_feed'),
]