import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import subprocess
import logging

# Add parent directory to path for imports FIRST
sys.path.insert(0, str(Path(__file__).parent.parent))

from bot.api_client import APIClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for FFmpeg
def check_ffmpeg():
    """Verify FFmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

load_dotenv()

if not check_ffmpeg():
    print("WARNING: FFmpeg not found in PATH. Voice features may not work.")
    print("Install FFmpeg and add it to your system PATH.")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.api = APIClient()  # Create API client instance on bot

@bot.listen()
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('------')
    print(f'Commands in tree: {len(bot.tree._get_all_commands())}')

async def load_cogs():
    """Load all cogs from bot/commands/ directory"""
    cogs_dir = Path(__file__).parent / 'commands'
    print(f'[*] Loading cogs from: {cogs_dir}')
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f'bot.commands.{cog_name}')
                print(f'[+] Loaded cog: {cog_name}')
            except Exception as e:
                print(f'[-] Failed to load {cog_name}: {e}')

async def setup_hook():
    """Load cogs and sync commands when bot is setting up"""
    print('[*] Running setup_hook()')
    await load_cogs()
    print('[*] About to sync slash commands...')
    try:
        synced = await bot.tree.sync()
        print(f'[+] Synced {len(synced)} slash command(s) globally')
        for cmd in synced:
            print(f'    - {cmd.name}')
    except Exception as e:
        print(f'[-] Failed to sync commands: {e}')
        import traceback
        traceback.print_exc()

# Manually set setup_hook (not as an event listener)
bot.setup_hook = setup_hook

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))