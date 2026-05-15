import discord
from discord.ext import commands
from discord import app_commands
from bot.api_client import APIClient

#Created using Cursor

class QueueCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = APIClient()
    
    @app_commands.command(name='play', description='Queue a song from YouTube and play if nothing is playing')
    async def play(self, interaction: discord.Interaction, url: str):
        """Queue a song from YouTube and play if nothing is playing"""
        try:
            await interaction.response.defer()
            print(f'[*] /play command invoked with URL: {url}')
            
            guild_id = str(interaction.guild.id)
            username = interaction.user.name
            
            print(f'[*] Guild ID: {guild_id}, User: {username}')
            
            # Extract song info from YouTube
            print(f'[*] Extracting song info from YouTube...')
            voice_cog = interaction.client.cogs.get('VoiceCommands')
            if voice_cog:
                song_info = await voice_cog.extract_song_info(url)
                if not song_info:
                    await interaction.followup.send('❌ Could not extract song info from URL')
                    return
                title = song_info['title']
                duration = song_info.get('duration', 0)
            else:
                title = 'Song'
                duration = 0
            
            print(f'[*] Song title: {title}')
            
            # Get or create queue
            queue = await self.api.get_queue(guild_id)
            if not queue:
                print('[*] Queue not found, creating new queue')
                queue = await self.api.create_queue(guild_id)
            
            print(f'[*] Adding song to queue')
            # Add song to queue with actual title
            song_data = await self.api.add_song(
                guild_id,
                title=title,
                url=url,
                added_by=username
            )
            
            if not song_data:
                print('[-] Failed to add song to queue')
                await interaction.followup.send('❌ Failed to add song to queue')
                return
            
            print(f'[+] Song added to queue')
            # Wrap URL in backticks to prevent Discord embed
            wrapped_url = f"`{url}`"
            
            # Check if anything is currently playing
            voice_client = interaction.guild.voice_client
            if voice_client and voice_client.is_playing():
                # Something is playing - just add to queue
                print('[*] Song queued (something already playing)')
                await interaction.followup.send(f'✅ Added to queue: **{title}**')
            else:
                # Nothing playing - start playing immediately
                print('[*] Queue was empty, added to queue')
                await interaction.followup.send(f'▶️ Now playing: **{title}**')
        except Exception as e:
            print(f'[-] Error in /play command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='queue', description='Display current queue')
    async def show_queue(self, interaction: discord.Interaction):
        """Display current queue"""
        try:
            await interaction.response.defer()
            print('[*] /queue command invoked')
            
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
            
            # Show total songs info
            embed.set_footer(text=f"Showing {min(len(remaining_songs), 10)} of {len(remaining_songs)} remaining songs")
            
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f'[-] Error in /queue command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')
    
    @app_commands.command(name='skip', description='Skip to next song')
    async def skip(self, interaction: discord.Interaction):
        """Skip to next song"""
        try:
            await interaction.response.defer()
            print('[*] /skip command invoked')
            
            guild_id = str(interaction.guild.id)
            print(f'[*] Guild ID: {guild_id}')
            
            result = await self.api.next_song(guild_id)
            print(f'[*] API response: {result}')
            
            if result:
                print('[+] Skip successful')
                await interaction.followup.send('⏭️ Skipped to next song')
            else:
                print('[-] Skip failed - API returned None')
                await interaction.followup.send('❌ Could not skip')
        except Exception as e:
            print(f'[-] Error in /skip command: {e}')
            import traceback
            traceback.print_exc()
            try:
                await interaction.followup.send(f'❌ Error: {str(e)}')
            except:
                print(f'[-] Failed to send error message')

    @app_commands.command(name='remove', description='Remove song at position')
    async def remove(self, interaction: discord.Interaction, position: int):
        """Remove song at position"""
        try:
            await interaction.response.defer()
            print(f'[*] /remove command invoked - position: {position}')
            
            guild_id = str(interaction.guild.id)
            queue = await self.api.get_queue(guild_id)
            
            if not queue or not queue.get('songs'):
                print('[-] Queue is empty')
                await interaction.followup.send('Queue is empty')
                return
            
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
    
    @app_commands.command(name='clear', description='Clear entire queue')
    async def clear(self, interaction: discord.Interaction):
        """Clear entire queue"""
        try:
            await interaction.response.defer()
            print('[*] /clear command invoked')
            
            guild_id = str(interaction.guild.id)
            print(f'[*] Clearing queue for guild {guild_id}')
            
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
    
    @app_commands.command(name='nowplaying', description='Show currently playing song')
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
