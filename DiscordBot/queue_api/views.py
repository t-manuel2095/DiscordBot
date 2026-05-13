from django.shortcuts import render
from django.http import HttpResponse
from queue_api.serializers import GuildQueueSerializer, SongSerializer
from .models import GuildQueue, Song
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response


# Create your views here.

class GuildQueueViewSet(viewsets.ModelViewSet):
    queryset = GuildQueue.objects.all()
    serializer_class = GuildQueueSerializer
    lookup_field = 'guild_id'

    #Add song to queue
    @action(detail=True, methods=['post'])
    def add_song(self, request, guild_id=None):
        queue = self.get_object()
        
        serializer = SongSerializer(data=request.data)
        if serializer.is_valid():
            # Calculate position
            last_song = queue.songs.order_by('-position').first()
            position = (last_song.position + 1) if last_song else 0
            
            serializer.save(queue=queue, position=position)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    #Get currently playing song
    @action(detail=True, methods=['get'])
    def current_song(self, request, guild_id=None):
        
        queue = self.get_object()
        song = queue.songs.filter(position=queue.current_song_index).first()
        if song:
            serializer = SongSerializer(song)
            return Response(serializer.data)
        return Response({'detail': 'No song currently playing'}, status=status.HTTP_404_NOT_FOUND)
    
    #Advance to next song
    @action(detail=True, methods=['post'])
    def next_song(self, request, guild_id=None):
        queue = self.get_object()
        queue.current_song_index += 1
        queue.save()
        return Response({'current_song_index': queue.current_song_index})

    
class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer

    #Delete a song and reorder remaining songs
    def destroy(self, request, *args, **kwargs):
        
        song = self.get_object()
        queue = song.queue
        deleted_position = song.position
        
        # Delete the song
        super().destroy(request, *args, **kwargs)
        
        # Reorder songs after deletion
        songs_after = queue.songs.filter(position__gt=deleted_position).order_by('position')
        for i, s in enumerate(songs_after):
            s.position = deleted_position + i
            s.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
