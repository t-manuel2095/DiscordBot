import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

#Created using Cursor

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = bot.api
        self.ydl_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch',
            'quiet': True,
            'no_warnings': True,
        }
        self.now_playing = {}  # Track what's playing: {guild_id: song_title}
        self.paused_state = {}  # Track paused guilds: {guild_id: True/False}
        self.keep_alive_tasks = {}  # Track keep-alive tasks: {guild_id: task}
    
    @app_commands.command(name='leave', description='Bot leaves the voice channel')
    async def leave(self, interaction: discord.Interaction):
        """Bot leaves the voice channel"""
        try:
            await interaction.response.defer()
            print('[*] /leave command invoked')
            
            if interaction.guild.voice_client:
                guild_id = str(interaction.guild.id)
                print(f'[*] Bot is in voice, disconnecting')
                await interaction.guild.voice_client.disconnect()
                
                # Clear the queue when leaving
                print(f'[*] Clearing queue for guild {guild_id}')
                await self.api.delete_queue(guild_id)
                
                # Cancel keep-alive task if exists
                if guild_id in self.keep_alive_tasks:
                    print('[*] Cancelling keep-alive task')
                    self.keep_alive_tasks[guild_id].cancel()
                    del self.keep_alive_tasks[guild_id]
                
                # Clear paused state
                self.paused_state.pop(guild_id, None)
                self.now_playing.pop(guild_id, None)
                
                print(f'[+] Queue cleared')
                await interaction.followup.send('Left voice channel and cleared queue')
            else:
                print('[-] Bot not in voice channel')
                await interaction.followup.send('Not connected to a voice channel')
        except Exception as e:
            print(f'[-] Error in /leave command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='pause', description='Pause audio playback')
    async def pause(self, interaction: discord.Interaction):
        """Pause audio playback"""
        try:
            await interaction.response.defer()
            print('[*] /pause command invoked')
            
            guild_id = str(interaction.guild.id)
            
            if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
                print('[*] Pausing playback')
                interaction.guild.voice_client.pause()
                self.paused_state[guild_id] = True
                
                # Start keep-alive task to prevent Discord from auto-disconnecting
                print('[*] Starting keep-alive task')
                self.keep_alive_tasks[guild_id] = asyncio.create_task(
                    self._keep_alive(guild_id, interaction.guild.voice_client)
                )
                
                print('[+] Playback paused')
                await interaction.followup.send('⏸️ Playback paused (bot will stay connected)')
            else:
                print('[-] Nothing is playing')
                await interaction.followup.send('Nothing is playing')
        except Exception as e:
            print(f'[-] Error in /pause command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='resume', description='Resume audio playback')
    async def resume(self, interaction: discord.Interaction):
        """Resume audio playback"""
        try:
            await interaction.response.defer()
            print('[*] /resume command invoked')
            
            guild_id = str(interaction.guild.id)
            
            if interaction.guild.voice_client and not interaction.guild.voice_client.is_playing():
                # Check if it's paused or just not playing
                if self.paused_state.get(guild_id):
                    print('[*] Resuming playback')
                    
                    # Cancel keep-alive task
                    if guild_id in self.keep_alive_tasks:
                        print('[*] Stopping keep-alive task')
                        self.keep_alive_tasks[guild_id].cancel()
                        del self.keep_alive_tasks[guild_id]
                    
                    interaction.guild.voice_client.resume()
                    self.paused_state[guild_id] = False
                    print('[+] Playback resumed')
                    await interaction.followup.send('▶️ Playback resumed')
                else:
                    print('[-] Nothing is paused')
                    await interaction.followup.send('Nothing is paused')
            else:
                print('[-] Already playing or not in voice')
                await interaction.followup.send('Already playing')
        except Exception as e:
            print(f'[-] Error in /resume command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    async def extract_song_info(self, url):
        """Extract song info (title, duration, audio_url) from YouTube URL"""
        try:
            print(f'[*] Extracting info from: {url}')
            with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', None)
                audio_url = info.get('url')  # This is the direct audio stream URL
                print(f'[+] Extracted - Title: {title}, Duration: {duration}')
                print(f'[*] Audio URL extracted: {audio_url[:50]}...' if audio_url else '[-] No audio URL')
                return {
                    'title': title,
                    'duration': duration,
                    'url': audio_url  # Store the audio stream URL, not YouTube URL
                }
        except Exception as e:
            print(f'[-] Error extracting song info: {e}')
            import traceback
            traceback.print_exc()
            return None
    
    async def play_audio(self, guild_id, voice_client):
        """Play audio for the current song in queue"""
        try:
            # Get current queue
            queue = await self.api.get_queue(guild_id)
            if not queue or not queue.get('songs'):
                print('[*] Queue is empty, stopping playback')
                self.now_playing[guild_id] = None
                return
            
            current_index = queue.get('current_song_index', 0)
            if current_index >= len(queue['songs']):
                print('[*] No more songs in queue')
                self.now_playing[guild_id] = None
                return
            
            current_song = queue['songs'][current_index]
            audio_url = current_song['url']  # This is already the audio stream URL
            title = current_song['title']
            
            if not audio_url:
                print('[-] No audio URL in queue song')
                return
            
            print(f'[*] Now playing: {title}')
            self.now_playing[guild_id] = title
            self.paused_state[guild_id] = False  # Reset paused state when starting playback
            
            # Create FFmpeg source with reconnection settings
            source = discord.FFmpegPCMAudio(
                audio_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
            
            # Create callback for when song finishes
            def after_callback(error):
                if error:
                    print(f'[-] Playback error: {error}')
                else:
                    print('[+] Song finished')
                    # Schedule next song using bot's event loop
                    try:
                        asyncio.run_coroutine_threadsafe(
                            self.play_next_in_queue(guild_id, voice_client),
                            self.bot.loop
                        )
                    except Exception as e:
                        print(f'[-] Error scheduling next song: {e}')
            
            # Play the audio
            voice_client.play(source, after=after_callback)
            print(f'[+] Started playing: {title}')
            
            # Send now playing message to a text channel
            try:
                # Get the guild
                guild = self.bot.get_guild(int(guild_id))
                if guild:
                    # Try to find a general channel or first text channel
                    text_channel = None
                    for channel in guild.text_channels:
                        if 'general' in channel.name.lower():
                            text_channel = channel
                            break
                    if not text_channel and guild.text_channels:
                        text_channel = guild.text_channels[0]
                    
                    if text_channel:
                        embed = discord.Embed(
                            title='🎵 Now Playing',
                            description=title,
                            color=discord.Color.green()
                        )
                        embed.add_field(name='Added by', value=current_song['added_by'])
                        if current_song.get('duration'):
                            minutes, seconds = divmod(current_song['duration'], 60)
                            embed.add_field(name='Duration', value=f'{minutes}:{seconds:02d}')
                        await text_channel.send(embed=embed)
            except Exception as e:
                print(f'[-] Error sending now playing message: {e}')
            
        except Exception as e:
            print(f'[-] Error playing audio: {e}')
            import traceback
            traceback.print_exc()
            
            # If it's an expired URL error, log it
            if 'googlevideo.com' in str(audio_url) and 'expire' in str(e).lower():
                print(f'[!] Audio stream URL may have expired, consider re-extracting from original')
            
            return
    
    async def play_next_in_queue(self, guild_id, voice_client):
        """Auto-advance to next song in queue"""
        try:
            print('[*] Auto-advancing to next song')
            # Skip to next
            result = await self.api.next_song(guild_id)
            if result:
                print(f'[+] Advanced to index {result.get("current_song_index")}')
                # Play the next song
                await self.play_audio(guild_id, voice_client)
            else:
                print('[-] Failed to advance queue')
        except Exception as e:
            print(f'[-] Error in auto-advance: {e}')
    
    @app_commands.command(name='repeat', description='Add current playing song to queue to play again')
    async def repeat(self, interaction: discord.Interaction):
        """Add current playing song to queue as next song (duplicate at position 2)"""
        try:
            await interaction.response.defer()
            print('[*] /repeat command invoked')
            
            guild_id = str(interaction.guild.id)
            
            # Get current queue
            queue = await self.api.get_queue(guild_id)
            if not queue or not queue.get('songs'):
                print('[-] Queue is empty')
                await interaction.followup.send('❌ Queue is empty')
                return
            
            current_index = queue.get('current_song_index', 0)
            if current_index >= len(queue['songs']):
                print('[-] No current song')
                await interaction.followup.send('❌ No song currently playing')
                return
            
            # Get the current song to repeat (only allow repeating the song currently playing)
            current_song = queue['songs'][current_index]
            song_title = current_song['title']
            song_url = current_song['url']
            
            # Calculate insertion position (right after current song)
            # Songs list is 0-indexed, but positions in API are based on database positions
            # We want to insert at current_index + 1
            insertion_position = current_index + 1
            
            print(f'[*] Repeating current song: {song_title}')
            print(f'[*] Inserting at position {insertion_position}')
            
            # Add current song again at the next position
            song_data = await self.api.add_song(
                guild_id,
                title=song_title,
                url=song_url,
                added_by=interaction.user.name,
                position=insertion_position
            )
            
            if song_data:
                print(f'[+] Song repeated and added to queue at position {insertion_position}')
                await interaction.followup.send(f'🔁 **{song_title}** will play again after current')
            else:
                print('[-] Failed to repeat song')
                await interaction.followup.send('❌ Failed to repeat song')
        except Exception as e:
            print(f'[-] Error in /repeat command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    async def _keep_alive(self, guild_id, voice_client):
        """Keep voice connection alive while paused to prevent auto-disconnect"""
        try:
            while self.paused_state.get(guild_id):
                await asyncio.sleep(30)  # Check every 30 seconds
                # Connection is kept alive just by maintaining the paused state
                # Discord won't disconnect as long as we're "active" in the channel
                print(f'[*] Keep-alive: Guild {guild_id} still paused')
        except asyncio.CancelledError:
            print('[*] Keep-alive task cancelled')
        except Exception as e:
            print(f'[-] Error in keep-alive: {e}')

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
