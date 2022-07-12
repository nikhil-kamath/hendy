import math
import discord
from discord.ext import commands, tasks
import os
import json
import random
import Utilities

'''
Class which takes care of repeated actions: 
    - speaking on a constant loop
    - percent chance to respond to users
'''
class Passive(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.loop_on = False   # if bot prints things on a loop
        self.loop_time = 60 # frequency (in minutes) of bot loop
        self.loop_channel = None # channel to loop in
        self.response_on = False # if bot has a chance to reply to any message
        self.response_chance = 3 # % chance for bot to respond randomly
        self.timer = math.inf
        
        self.res_folder = './resources'
        self.passive_file = 'passive.json'
        
        self.require_auth = True # whether or not changing passive settings requires authorization
        
        with open(os.path.join(self.res_folder, self.passive_file)) as file:
            data = json.load(file)
            self.loop_time = data['loop_time']
            self.response_chance = data['response_chance']
    
    '''toggle loop, saving the channel in which the command was called in'''
    @commands.command()
    async def toggle(self, ctx):
        if self.require_auth:
            admins = self.bot.get_cog('Admins')
            if admins is not None and not admins.is_authorized(ctx.author.id):
                admins.unauthorized_message(ctx, "toggle")
                return

        self.loop_channel = ctx
        self.loop_on = not self.loop_on
        if self.loop_on:
            await ctx.send("me loopig")
        else:
            await ctx.send("me no longer looping")
    
    '''random chance to respond to user's messages'''
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user: # response cannot trigger on bot messages
            return

        if self.response_on and random.randint(1, 100) <= self.response_chance:
            statements = self.bot.get_cog("Statements")
            statements.speak(message.channel)

    '''looping with object's loop_time'''
    @tasks.loop(seconds=1)
    async def loop(self):
        if not self.loop_on: return
        
        self.timer -= 1
        self.timer = min(self.timer, self.loop_time)
        if self.timer > 0: return
        
        '''speak'''
        self.timer = self.loop_time
        
        
    '''change response chance'''
    @commands.command()
    async def chance(self, ctx, new):
        self.response_chance = int(new)
        self.save()
    
    '''change loop time'''
    @commands.command()
    async def looptime(self, ctx, new):
        self.loop_time = int(new)
        self.save()
    
    '''save object data to json file'''
    def save(self):
        data = {"response_chance": self.response_chance, "loop_time": self.loop_time}
        Utilities.store(os.path.join(self.res_folder, self.passive_file), data)


def setup(bot):
    bot.add_cog(Passive(bot))
