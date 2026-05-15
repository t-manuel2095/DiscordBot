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
    
    @app_commands.command(name='join', description='Bot joins the voice channel')
    async def join(self, interaction: discord.Interaction):
        """Bot joins the voice channel"""
        try:
            await interaction.response.defer()
            print('[*] /join command invoked')
            
            if not interaction.user.voice:
                print('[-] User not in voice channel')
                await interaction.followup.send('You must be in a voice channel')
                return
            
            channel = interaction.user.voice.channel
            print(f'[*] User is in channel: {channel.name}')
            
            print(f'[*] Attempting to connect to {channel.name}')
            await channel.connect()
            print(f'[+] Connected to {channel.name}')
            await interaction.followup.send(f'Joined {channel.name}')
        except Exception as e:
            print(f'[-] Error in /join command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Could not join channel: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
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
                print(f'[+] Queue cleared')
                
                print(f'[+] Disconnected from voice')
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
    
    @app_commands.command(name='stop', description='Stop audio playback')
    async def stop(self, interaction: discord.Interaction):
        """Stop audio playback"""
        try:
            await interaction.response.defer()
            print('[*] /stop command invoked')
            
            if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
                print('[*] Stopping playback')
                interaction.guild.voice_client.stop()
                print('[+] Playback stopped')
                await interaction.followup.send('⏹️ Playback stopped')
            else:
                print('[-] Nothing is playing')
                await interaction.followup.send('Nothing is playing')
        except Exception as e:
            print(f'[-] Error in /stop command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    def extract_audio_url(self, url):
        """Extract audio stream URL from YouTube"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                return info['url'], info['title']
        except Exception as e:
            return None, None
    
    async def extract_song_info(self, url):
        """Extract song info (title, duration) from YouTube URL"""
        try:
            print(f'[*] Extracting info from: {url}')
            with yt_dlp.YoutubeDL(self.ydl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', None)
                print(f'[+] Extracted - Title: {title}, Duration: {duration}')
                return {
                    'title': title,
                    'duration': duration,
                    'url': info.get('url')
                }
        except Exception as e:
            print(f'[-] Error extracting song info: {e}')
            return None

async def setup(bot):
    await bot.add_cog(VoiceCommands(bot))
