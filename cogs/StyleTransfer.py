import asyncio
from discord.ext import commands
from discord.ext.commands.context import Context
import concurrent.futures
from utilities.style_transfer.NST import style_transfer
import discord

class StyleTransfer(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.transferring = False
    
    @commands.command()
    async def transfer(self, ctx: Context, image_link):
        if self.transferring:
            await ctx.send("sorry, hendy's already working on one style transfer")
            return
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            self.transferring = True
            await ctx.send("processing image!")
            loop = asyncio.get_running_loop()
            output_directory = await loop.run_in_executor(pool, style_transfer, image_link)
            
            with open(output_directory, 'rb') as file:
                output = discord.File(file)
                await ctx.send(file=output)
            
            self.transferring = False
            


def setup(bot):
    bot.add_cog(StyleTransfer(bot))