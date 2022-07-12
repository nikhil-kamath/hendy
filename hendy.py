import discord
import random
import json
import os
from discord.ext import tasks
from discord.ext import commands
import pandas as pd


bot = commands.Bot(command_prefix='.')
cogs = ['Admins',
        'Misc',
        'Passive',
        'Statements',
        'Youtube']
for cog in cogs:
    bot.load_extension(cog)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    
bot.run("ODMxODk0MjYzMjU1MjY5NDE3.GfgSKR.Ehxu3UTwuPsGyQNiAp1wF8X3tVf3oaA-0L3Y3M")
