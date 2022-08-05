import asyncio
import concurrent.futures
import logging
import os
import random
from threading import Thread

import config
import discord
import pandas as pd
import utilities.Comments as Comments
from discord.ext import commands, tasks
# from utilities.ytcomments import process_youtube_comments
from googleapiclient.discovery import build
from utilities.Utilities import save_dataframe_as_pickle
from utilities.Database import create_table, create_entry, random_rows, get_row

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
        
        self.database_name = "hendy"
        self.table_prefix = "yt_"
        
        # initialize comments from current pickle files
        files = [f for f in os.listdir(os.path.join(self.res_folder, self.yt_folder)) if os.path.isfile(os.path.join(self.res_folder, self.yt_folder, f))]
        for f in files:
            temp = pd.read_pickle(os.path.join(self.res_folder, self.yt_folder, f))
            self.comments = pd.concat([self.comments, temp], ignore_index=True)
        
        if len(self.comments) > 10:    
            print(self.comments.sample(10))
    
    @commands.command()
    async def moreinfo(self, ctx, *, com) -> None:
        """get more info about a previous comment

        Args:
            ctx (_type_): context
            com (_type_): comment 

        Returns:
            _type_: _description_
        """
        result = get_row(self.table_prefix + str(ctx.guild.id), self.database_name, 
                         "comment", com)
        if result:
            for key, value in result.items():
                if key == "Id": continue
                await ctx.send(f"**{key}:** {value}")
        else:
            await ctx.send("sorry comment not found")
        
        
    '''send random message from comments DataFrame'''
    @commands.command(aliases=['y', 'yt'])
    async def comment(self, ctx):            
        output = random_rows(self.table_prefix + str(ctx.guild.id), self.database_name)
        if output:
            logging.info("got result from sql")
            await ctx.send(output['comment'])
        else:
            logging.warning("sql did not return a result, defaulting to pkl backups")
            await ctx.send(str(self.comments['comment'][random.randrange(0, self.comments.shape[0])]))
    
        
    '''use a youtube search to find videos with a given query and take comments from them
    creates new event loop so that bot is still running during query'''
    @commands.command()
    async def searchyt(self, ctx, *, query):
        loop = asyncio.get_running_loop()
        
        # run in another threadpool
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await ctx.send(f"searching youtube for *{query}*")
            
            # sync call to get comments dataframe and store them in the database
            new_comments = await loop.run_in_executor(pool, self.find_comments, query)
            await loop.run_in_executor(pool, self.store_comments, new_comments, self.table_prefix + str(ctx.guild.id))
            
            # create output message using unique video titles and their corresponding channels
            output_message = f"**added {len(new_comments)} comments from search '{query}'.**\n"
            output_message += "**videos include:**\n"
            for _, row in new_comments.groupby("video", as_index=False).first().iterrows():
                output_message += f"**{row['channel']}**: {row['video'][:30]}...\n"
            
            self.comments = pd.concat([self.comments, new_comments], ignore_index=True)
            save_dataframe_as_pickle("./resources/yt", f"query.{query}{random.randrange(100000, 1000000)}.pkl", new_comments)
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
    
    
    def store_comments(self, comments:pd.DataFrame, table_name:str) -> None:
        data_types = [(column, 500) for column in comments.columns]
        create_table(table_name, self.database_name, data_types)
        for _, row in comments.iterrows():
            create_entry(table_name, self.database_name, row)
            
    
    
def setup(bot):  # sourcery skip: instance-method-first-arg-name
    bot.add_cog(Youtube(bot))
