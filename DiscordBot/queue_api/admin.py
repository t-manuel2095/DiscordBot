from django.contrib import admin
from .models import GuildQueue, Song

# Register your models here.
admin.site.register(GuildQueue)
admin.site.register(Song)