import discord
from discord.ext import commands, tasks
import os
import random

'''
class to handle miscellaneous tasks
'''
class Miscellaneous(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    '''clear certain number of chat messages'''
    @commands.command()
    async def clear(self, ctx, amount: int=10):
        admins = self.bot.get_cog("Admins")
        if not admins.is_authorized(ctx.author.id):
            admins.unauthorized_message(ctx, "clear")
        
        await ctx.channel.purge(limit=amount)
    
    '''legit just yes or no coin flip kinda deal'''
    @commands.command()
    async def yn(self, ctx, *, message=None):
        if message is None:
            await ctx.send(random.choice(['yes', 'no']))
            return
        await ctx.send(random.choice([f"{message}? YES", f"{message}? NO"]))
    
    '''no idea ngl'''
    @commands.command()
    async def spitfacts(self, ctx):
        await ctx.channel.send(random.choice(
            ['no', 'ok', 'sure thing', 'gimme a sec', '1s', 'brb then i will', 'yea wait a bit tho', 'getting on',
            'i will later']))


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
