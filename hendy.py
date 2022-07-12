import discord
import random
import json
import os
from discord.ext import tasks
from discord.ext import commands
import pandas as pd
import config


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
    
bot.run(config.bot_token)
