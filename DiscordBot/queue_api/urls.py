from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GuildQueueViewSet, SongViewSet

router = DefaultRouter()
router.register(r'queues', GuildQueueViewSet, basename='guild-queue')
router.register(r'songs', SongViewSet, basename='song')

urlpatterns = [
    path('', include(router.urls))    
]