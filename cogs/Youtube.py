import asyncio
import logging
import discord
from discord.ext import commands, tasks
import os
import random
import pandas as pd
# from utilities.ytcomments import process_youtube_comments
from googleapiclient.discovery import build
import utilities.Comments as Comments
import config
from threading import Thread
import concurrent.futures

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
    creates new event loop so that bot is still running dlduring query'''
    @commands.command()
    async def searchyt(self, ctx, *, query):
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await ctx.send(f"searching youtube for *{query}*")
            
            new_comments = await loop.run_in_executor(pool, self.find_comments, query)
            
            output_message = f"**added {len(new_comments)} comments from search '{query}'.**\n"
            output_message += "**videos include:**\n"
            for _, row in new_comments.groupby("video", as_index=False).first().iterrows():
                output_message += row["channel"] + ": " + row["video"] + "\n"
            
            # self.comments = pd.concat([self.comments, new_comments], ignore_index=True)
            print(new_comments.head())
            print(new_comments.tail())
            await ctx.send(output_message)
            
        

    '''processes youtube comments in other task'''
    async def search_yt_helper(self, ctx, query):     
        # await asyncio.sleep(30) # this version works so theres an issue with the Comments module eating the loop
        # await confirmation_ctx.send(f"got results from {query}")
        # return   
        # get video ids and titles from Comments package
        await ctx.send(f"searching youtube for {query}") # send confirmation to discord channel
        video_ids, video_titles, channels = await Comments.youtube_search_keyword(self.api_key, query, max_results=5)
        n = 0
        new_comments = pd.DataFrame()
        logging.info(f"got {len(video_ids)} results")
        # for each video, get comments from id and add them to new_comments dataframe
        for v_id in video_ids:
            c = await Comments.youtube_get_comments(self.api_key, v_id, scrolls=3)
            n += len(c)
            temp = pd.DataFrame(c, columns=['comment'])
            new_comments = pd.concat([new_comments, temp], ignore_index=True)
            
        print(f"added {n} comments from query")

        # create output message using the video titles returned by Comments package
        output_message = f"**added {len(new_comments)} comments from search '{query}'.**\n"
        output_message += "**videos include:** \n"
        for channel, title in zip(channels, video_titles):
            output_message += channel + ": " + title + "\n"
        
        # add new comments to Youtube cog's comments df
        self.comments = pd.concat([new_comments, self.comments], ignore_index=True)
        
        # save new comments to pickle file
        outdir = './resources/yt'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
            
        filename = "query." + query + ".pkl"
        new_comments.to_pickle(os.path.join(outdir, filename))
        
        # send confirmation in original discord channel
        await ctx.send(output_message)


    def find_comments(self, query: str) -> pd.DataFrame:
        """sync method to find comments

        Args:
            query (_type_): query
        """
        video_ids, video_titles, channels = Comments.youtube_search_keyword(self.api_key, query)
        new_comments = pd.DataFrame()
        for video_id, video_title, channel in zip(video_ids, video_titles, channels):
            data = {"comment": Comments.youtube_get_comments(self.api_key, video_id, scrolls=3)}
            data["video"] = [video_title]*len(data["comment"])
            data["channel"] = [channel]*len(data["comment"])
            
            new_comments = pd.concat([new_comments, pd.DataFrame(data)], ignore_index=True)
        return new_comments
    
    
    
def setup(bot):  # sourcery skip: instance-method-first-arg-name
    bot.add_cog(Youtube(bot))
