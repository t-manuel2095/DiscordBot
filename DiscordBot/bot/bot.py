import discord
from discord.ext import commands
import os

class MusicBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Basic ping command to test bot connectivity"""
        await ctx.send('Pong!')
    
    @commands.command(name='hello')
    async def hello(self, ctx):
        """Test command"""
        await ctx.send(f'Hello {ctx.author.name}!')

async def setup(bot):
    await bot.add_cog(MusicBot(bot))
