"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from posts.views import hello_world, like_post, comment_post, get_comments, custom_register, custom_login, google_oauth_login, google_oauth_callback, google_oauth_exchange, login_page, dashboard_view, dashboard_stats, recent_activity, news_feed
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', login_page, name='root'),  # Direct to login page
    path('admin/', admin.site.urls),
    path('hello/', hello_world),
    
    # User login page
    path('login/', login_page, name='login_page'),
    
    # Custom Authentication endpoints (return full user details)
    path('auth/registration/', custom_register, name='custom_register'),
    path('auth/login/', custom_login, name='custom_login'),
    path('auth/google/login/', google_oauth_login, name='google_oauth_login'),
    path('auth/google/callback/', google_oauth_callback, name='google_oauth_callback'),
    path('auth/google/exchange/', google_oauth_exchange, name='google_oauth_exchange'),
    
    # Standard auth endpoints
    path('auth/', include('dj_rest_auth.urls')),
    path('auth/google/', include('allauth.socialaccount.urls')),
    path('accounts/', include('allauth.urls')),

    # Post endpoints
    path('posts/<int:id>/like/', like_post),
    path('posts/<int:id>/comment/', comment_post),
    path('posts/<int:id>/comments/', get_comments),
    
    # Dashboard page and API endpoints
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('api/dashboard/activity/', recent_activity, name='recent_activity'),
    
    # News feed endpoint
    path('api/feed/', news_feed, name='news_feed'),
]

# Static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
