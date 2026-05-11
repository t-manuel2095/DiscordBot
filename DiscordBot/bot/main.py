import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
#Discord intents are permissions that tell Discord what events your bot wants to receive.

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
#This is a Discord event listener
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print('------')

#Looks in the commands folder and loads all the commands
async def load_cogs():
    for filename in os.listdir('./bot/commands'):
        if filename.endswith('.py'):
            await bot.load_extension(f'bot.commands.{filename[:-3]}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())