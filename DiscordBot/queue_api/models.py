from django.db import models
from django.db.models.fields import related

# Create your models here.
class GuildQueue(models.Model):
    guild_id = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_playing = models.BooleanField(default=False)
    current_song_index = models.IntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.guild_id

class Song(models.Model):
    queue = models.ForeignKey(GuildQueue, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=255)
    url = models.TextField()  # Changed from URLField to TextField to support long audio stream URLs
    added_by = models.CharField(max_length=255)
    position = models.IntegerField()
    duration = models.IntegerField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['position']
        unique_together = ['queue', 'position']

    def __str__(self):
        return self.title