import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

print('[!] Creating bot...')

@bot.event
async def setup_hook():
    print('[SETUP_HOOK] Called!')

@bot.event  
async def on_ready():
    print(f'[ON_READY] {bot.user}')
    print(f'[ON_READY] Commands in tree: {len(bot.tree._get_all_commands())}')

print('[!] Starting bot...')
bot.run(os.getenv('DISCORD_BOT_TOKEN'))
