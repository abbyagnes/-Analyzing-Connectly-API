from django.contrib import admin
from .models import Post, Like, Comment, UserProfile

admin.site.register(Post)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(UserProfile)
