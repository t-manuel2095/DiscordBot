"""
Definition of urls for DiscordBot.
"""
from django.urls import path
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
]
