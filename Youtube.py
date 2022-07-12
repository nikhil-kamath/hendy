import discord
from discord.ext import commands, tasks
import os
import random
import pandas as pd
from ytcomments import process_youtube_comments


'''
Class which allows users to add comments from a youtube video
Takes care of:
    - scraping comments from given link
    - storing comments in dataframe unique to each video
    - choosing random comment from collection of all comments
'''
class Youtube(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.comments = pd.DataFrame()
        
        self.res_folder = './resources'
        self.yt_folder = "yt"
        files = [f for f in os.listdir(os.path.join(self.res_folder, self.yt_folder)) if os.path.isfile(os.path.join(self.res_folder, self.yt_folder, f))]
        for f in files:
            temp = pd.read_pickle(os.path.join(self.res_folder, self.yt_folder, f))
            self.comments = pd.concat([self.comments, temp], ignore_index=True)
    
    '''send random message from comments DataFrame'''
    @commands.command(aliases=['y'])
    async def comment(self, ctx):
        await ctx.send(str(self.comments['comment'][random.randrange(0, self.comments.shape[0])]))
    
    '''scrape comments from input youtube link, create new df and append to comments'''
    @commands.command()
    async def addyt(self, ctx, link):
        await ctx.send("collecting comments from youtube link")
        temp, title = process_youtube_comments(link)
        comments = pd.concat([comments, temp], ignore_index=True)
        await ctx.send(f"added {len(temp)} comments from {title}")


def setup(bot):
    bot.add_cog(Youtube(bot))
