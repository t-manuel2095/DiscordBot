from rest_framework import serializers
from .models import GuildQueue, Song

class SongSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Song
        fields = ('id','queue','title','url','added_by','position','duration','added_at')
        read_only_fields = ('id', 'added_at')

class GuildQueueSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)

    class Meta: 
        model = GuildQueue
        fields = ('id', 'guild_id', 'created_at', 'updated_at', 'is_playing', 'current_song_index', 'songs')
        read_only_fields = ('id', 'created_at', 'updated_at')