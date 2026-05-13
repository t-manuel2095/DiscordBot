"""This file was primarily created by cursor"""

from rest_framework import serializers
from .models import GuildQueue, Song
import re

def normalize_youtube_url(url):
    """
    Normalize various YouTube URL formats to standard format.
    Handles: youtube.com, youtu.be, www.youtube.com, etc.
    """
    # Extract video ID using regex patterns
    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'([a-zA-Z0-9_-]{11})',  # Just the video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f'https://www.youtube.com/watch?v={video_id}'
    
    raise serializers.ValidationError('Invalid YouTube URL format. Please provide a valid YouTube URL.')

class SongSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Song
        fields = ('id','queue','title','url','added_by','position','duration','added_at')
        read_only_fields = ('id', 'added_at', 'queue', 'position')
    
    def to_internal_value(self, data):
        """Normalize YouTube URL before field validation."""
        if 'url' in data:
            data['url'] = normalize_youtube_url(data['url'])
        return super().to_internal_value(data)

class GuildQueueSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)

    class Meta: 
        model = GuildQueue
        fields = ('id', 'guild_id', 'created_at', 'updated_at', 'is_playing', 'current_song_index', 'songs')
        read_only_fields = ('id', 'created_at', 'updated_at')