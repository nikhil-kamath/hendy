import discord
from discord.ext import commands, tasks
import re
import os
import utilities.Utilities as Utilities

'''Class to keep track of 'authorized' users'''
class Admins(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.authorized = set()
        self.res_folder = './resources'
        self.auth_file = 'auth.txt'
        # load auth.txt and authorized users
        with open(os.path.join(self.res_folder, self.auth_file), 'r') as file:
            lines = file.readlines()
            for line in lines:
                self.authorized.add(int(line.strip()))
                        
    
    @commands.command(aliases=['op'])
    async def auth(self, ctx, member):
        mention = member
        member_id = int(re.sub('[<>@!]', '', member)) # get the member id
        
        if ctx.author.id not in self.authorized: return # unauthorized users cannot authorize others
        
        if member_id in self.authorized: # target already authorized
            await ctx.send(f'{mention} is already authorized')
            return
        
        with open('auth.txt', 'a') as f:
            f.write(str(member_id) + '\n')
        self.authorized.add(member_id)
        
        await ctx.send(f"{mention} has been authorized yipee")
    
    @commands.command(aliases=['deop'])
    async def deauth(self, ctx, member):
        mention = member
        member_id = int(re.sub('[<>@!]', '', member))
        
        if ctx.author.id not in self.authorized: return # unauthorized users cannot deauthorize
        if ctx.author.id == member_id: return # people cannot deauthorize themselves
        
        if member_id not in self.authorized: # deauthorizing someone who is not authorized in the first place
            await ctx.send(f"{mention} is not authorized")
            return

        Utilities.f_remove(os.path.join(self.res_folder, self.auth_file), str(member_id))
        self.authorized.remove(member_id)
        await ctx.send(f"{mention} has been deauthorized")
        
    async def is_authorized(self, target): # returns whether target is authorized
        return target in self.authorized
    
    async def unauthorized_message(self, ctx, command_name): # methods to send not authorized message for certain command
        await ctx.send(f"You are not authorized to use the **{command_name}** command")
        
def setup(bot):
    bot.add_cog(Admins(bot))