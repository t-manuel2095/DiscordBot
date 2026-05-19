import discord
from discord.ext import commands
from discord import app_commands
from bot.api_client import APIClient
import asyncio
import re

#Created using Cursor

class QueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = APIClient()
    
    @app_commands.command(name='pplay', description='Queue a song from YouTube and play if nothing is playing')
    async def play(self, interaction: discord.Interaction, query: str):
        """Queue a song from YouTube and play if nothing is playing"""
        try:
            await interaction.response.defer()
            print(f'[*] /pplay command invoked with query: {query}')
            
            guild_id = str(interaction.guild.id)
            username = interaction.user.name
            
            print(f'[*] Guild ID: {guild_id}, User: {username}')
            
            # Check if input is a URL or a search string
            url_pattern = r'https?://(www\.)?(youtube\.com|youtu\.be)'
            is_url = re.match(url_pattern, query)
            
            # If it's a search string, append "lyrics" if not already present
            search_query = query
            if not is_url:
                if not search_query.lower().endswith('lyrics'):
                    search_query = f"{search_query} lyrics"
                    print(f'[*] Modified search query: {search_query}')
            
            # Check if bot is in voice channel, if not auto-join user's channel
            if not interaction.guild.voice_client:
                if not interaction.user.voice:
                    await interaction.followup.send('❌ You must be in a voice channel to play music')
                    return
                
                channel = interaction.user.voice.channel
                print(f'[*] Bot not in voice, auto-joining: {channel.name}')
                try:
                    await channel.connect()
                    print(f'[+] Auto-joined {channel.name}')
                except Exception as e:
                    print(f'[-] Failed to auto-join: {e}')
                    await interaction.followup.send(f'❌ Could not join voice channel: {str(e)}')
                    return
            
            # Extract song info from YouTube
            print(f'[*] Extracting song info from YouTube...')
            voice_cog = interaction.client.cogs.get('VoiceCommands')
            if voice_cog:
                song_info = await voice_cog.extract_song_info(search_query)
                if not song_info:
                    await interaction.followup.send('❌ Could not extract song info from URL or search query')
                    return
                title = song_info['title']
                duration = song_info.get('duration', 0)
                audio_url = song_info.get('url')  # Get the actual audio stream URL
                
                # Check if song is longer than 10 minutes (600 seconds)
                if duration and duration > 600:
                    minutes = duration // 60
                    await interaction.followup.send(f'❌ Song is too long ({minutes} minutes). Maximum length is 10 minutes.')
                    print(f'[-] Song rejected: Duration {minutes} minutes exceeds 10 minute limit')
                    return
            else:
                title = 'Song'
                duration = 0
                audio_url = search_query
            
            print(f'[*] Song title: {title}')
            
            # Get or create queue
            queue = await self.api.get_queue(guild_id)
            if not queue:
                print('[*] Queue not found, creating new queue')
                queue = await self.api.create_queue(guild_id)
            
            print(f'[*] Adding song to queue')
            print(f'[*] Audio URL to send: {audio_url[:80] if audio_url else "None"}...')
            # Add song to queue with actual title and audio stream URL
            song_data = await self.api.add_song(
                guild_id,
                title=title,
                url=audio_url,  # Send the audio stream URL, not YouTube URL
                added_by=username
            )
            
            if not song_data:
                print('[-] Failed to add song to queue')
                await interaction.followup.send('❌ Failed to add song to queue')
                return
            
            print(f'[+] Song added to queue')
            
            # Check if anything is currently playing
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                # Something is playing - just add to queue
                print('[*] Song queued (something already playing)')
                await interaction.followup.send(f'✅ Added to queue: **{title}**')
            else:
                # Nothing playing - start playing immediately
                print('[*] Queue was empty, starting playback')
                await interaction.followup.send(f'▶️ Now playing: **{title}**')
                
                # Start playback in background
                if voice_client:
                    print('[*] Starting audio playback')
                    voice_cog = interaction.client.cogs.get('VoiceCommands')
                    if voice_cog:
                        asyncio.create_task(voice_cog.play_audio(guild_id, voice_client))
        except Exception as e:
            print(f'[-] Error in /pplay command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='qqueue', description='Display current queue')
    async def show_queue(self, interaction: discord.Interaction):
        """Display current queue"""
        try:
            await interaction.response.defer()
            print('[*] /qqueue command invoked')
            
            guild_id = str(interaction.guild.id)
            queue = await self.api.get_queue(guild_id)
            
            if not queue or not queue.get('songs'):
                await interaction.followup.send('Queue is empty')
                return
            
            current_index = queue.get('current_song_index', 0)
            print(f'[*] Current song index: {current_index}')
            
            # Get songs from current index onwards
            remaining_songs = queue['songs'][current_index:]
            
            if not remaining_songs:
                await interaction.followup.send('No songs remaining in queue')
                return
            
            embed = discord.Embed(title='🎵 Queue (Remaining Songs)', color=discord.Color.blue())
            for idx, song in enumerate(remaining_songs[:10]):
                # First song is always currently playing
                if idx == 0:
                    name = f"▶️ {idx + 1}. {song['title']} (NOW PLAYING)"
                else:
                    name = f"{idx + 1}. {song['title']}"
                
                embed.add_field(
                    name=name,
                    value=f"Added by: {song['added_by']}",
                    inline=False
                )
            
            if len(remaining_songs) > 10:
                embed.add_field(name='...', value=f"+{len(remaining_songs) - 10} more songs")
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f'[-] Error in /queue command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='sskip', description='Skip to next song')
    async def skip(self, interaction: discord.Interaction):
        """Skip to next song"""
        try:
            await interaction.response.defer()
            print('[*] /sskip command invoked')
            
            guild_id = str(interaction.guild.id)
            
            # Just stop the current playback
            # The after-callback will automatically call play_next_in_queue()
            # which will handle advancing the index and playing next song
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                print('[*] Stopping current playback to skip')
                voice_client.stop()  # This triggers after_callback → play_next_in_queue()
                await interaction.followup.send('⏭️ Skipped to next song')
            else:
                print('[-] Nothing is playing to skip')
                await interaction.followup.send('❌ Nothing is playing')
        except Exception as e:
            print(f'[-] Error in /skip command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')

    @app_commands.command(name='rremove', description='Remove song at position')
    async def remove(self, interaction: discord.Interaction, position: int):
        """Remove song at position"""
        try:
            await interaction.response.defer()
            print(f'[*] /rremove command invoked - position: {position}')
            
            guild_id = str(interaction.guild.id)
            queue = await self.api.get_queue(guild_id)
            
            if not queue or not queue.get('songs'):
                print('[-] Queue is empty')
                await interaction.followup.send('Queue is empty')
                return
            
            current_index = queue.get('current_song_index', 0)
            
            # Check if position is valid
            if position < 1 or position > len(queue['songs']):
                print(f'[-] Invalid position: {position}')
                await interaction.followup.send(f'❌ Position must be between 1 and {len(queue["songs"])}')
                return
            
            # Get the song to delete (positions are 1-indexed)
            song_to_delete = queue['songs'][position - 1]
            song_id = song_to_delete['id']
            
            print(f'[*] Deleting song ID: {song_id}')
            success = await self.api.delete_song(song_id)
            
            if success:
                print(f'[+] Song removed')
                
                # If we removed the currently playing song, stop playback and play next
                if position - 1 == current_index:
                    print('[*] Removed song is currently playing, stopping playback')
                    voice_client = interaction.guild.voice_client
                    if voice_client and voice_client.is_playing():
                        voice_client.stop()  # Will trigger after_callback to play next
                
                await interaction.followup.send(f'✅ Removed song at position {position}')
            else:
                print('[-] Delete failed')
                await interaction.followup.send('❌ Failed to remove song')
        except Exception as e:
            print(f'[-] Error in /remove command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='cclear', description='Clear entire queue')
    async def clear(self, interaction: discord.Interaction):
        """Clear entire queue"""
        try:
            await interaction.response.defer()
            print('[*] /cclear command invoked')
            
            guild_id = str(interaction.guild.id)
            print(f'[*] Clearing queue for guild {guild_id}')
            
            # Stop playback first
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                print('[*] Stopping playback before clearing queue')
                voice_client.stop()
            
            success = await self.api.delete_queue(guild_id)
            
            if success:
                print('[+] Queue cleared')
                await interaction.followup.send('✅ Queue cleared')
            else:
                print('[-] Clear failed')
                await interaction.followup.send('❌ Failed to clear queue')
        except Exception as e:
            print(f'[-] Error in /clear command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='nnowplaying', description='Show currently playing song')
    async def now_playing(self, interaction: discord.Interaction):
        """Show currently playing song"""
        await interaction.response.defer()
        
        guild_id = str(interaction.guild.id)
        queue = await self.api.get_queue(guild_id)
        
        if queue and queue['songs']:
            current = queue['songs'][queue['current_song_index']]
            embed = discord.Embed(
                title='🎵 Now Playing',
                description=current['title'],
                color=discord.Color.green()
            )
            embed.add_field(name='Added by', value=current['added_by'])
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send('Nothing is playing')

async def setup(bot):
    await bot.add_cog(QueueCommands(bot))
