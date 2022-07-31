import asyncio
import discord
from discord.ext import commands, tasks
import os
import random
import pandas as pd
# from utilities.ytcomments import process_youtube_comments
from googleapiclient.discovery import build
import utilities.Comments as Comments
import config


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
        
        self.api_key = config.youtube_api_key
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
    
    # '''scrape comments from input youtube link, create new df and append to comments'''
    # @commands.command()
    # async def addyt(self, ctx, link):
    #     await ctx.send("collecting comments from youtube link")
    #     temp, title = process_youtube_comments(link)        
    #     self.comments = pd.concat([self.comments, temp], ignore_index=True)
    #     await ctx.send(f"added {len(temp)} comments from {title}")
        
    '''use a youtube search to find videos with a given query and take comments from them
    creates new event loop so that bot is still running during query'''
    @commands.command()
    async def searchyt(self, ctx, *, query):
        await ctx.send(f"searching youtube for {query}") # send confirmation to discord channel
        asyncio.create_task(self.search_yt_helper(query, ctx))
        

    '''processes youtube comments in other task'''
    async def search_yt_helper(self, query, confirmation_ctx):
        # create call to youtube api
        yt = build('youtube', 'v3', developerKey=self.api_key)
        
        # get video ids and titles from Comments package
        video_ids, video_titles = await Comments.youtube_search_keyword(yt, query, max_results=5)
        n = 0
        new_comments = pd.DataFrame()
        
        # for each video, get comments from id and add them to new_comments dataframe
        for v_id in video_ids:
            c = await Comments.youtube_get_comments(yt, v_id, scrolls=3)
            n += len(c)
            temp = pd.DataFrame(c, columns=['comment'])
            new_comments = pd.concat([new_comments, temp], ignore_index=True)
            
        print(f"added {n} comments from query")

        # create output message using the video titles returned by Comments package
        output_message = f"**added {len(new_comments)} comments from search '{query}'.**\n"
        output_message += "**videos include:** \n"
        for title in video_titles:
            output_message += title + "\n"
        
        # add new comments to Youtube cog's comments df
        self.comments = pd.concat([new_comments, self.comments], ignore_index=True)
        
        # save new comments to pickle file
        outdir = './resources/yt'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            
        filename = "query." + query + ".pkl"
        new_comments.to_pickle(os.path.join(outdir, filename))
        
        # send confirmation in original discord channel
        await confirmation_ctx.send(output_message)
        
def setup(bot):  # sourcery skip: instance-method-first-arg-name
    bot.add_cog(Youtube(bot))
