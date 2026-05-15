import asyncio
import discord
from bot.api_client import APIClient

#Created via Cursor

class QueueManager:
    def __init__(self, bot):
        self.bot = bot
        self.api = APIClient()
        self.now_playing = {}
    
    async def play_next(self, ctx, guild_id):
        """Play next song in queue"""
        guild_id_str = str(guild_id)
        
        queue = await self.api.get_queue(guild_id_str)
        if not queue or not queue.get('songs'):
            await ctx.send('Queue is empty')
            return
        
        # Get current song
        current_idx = queue['current_song_index']
        songs = queue['songs']
        
        if current_idx >= len(songs):
            await ctx.send('End of queue reached')
            return
        
        current_song = songs[current_idx]
        self.now_playing[guild_id] = current_song
        
        await ctx.send(f'🎵 Now playing: **{current_song["title"]}** (by {current_song["added_by"]})')
    
    async def auto_advance(self, guild_id):
        """Automatically advance queue"""
        await self.api.next_song(str(guild_id))
