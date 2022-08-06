import asyncio
from discord.ext import commands

class StyleTransfer(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def transfer(self, ctx, image_link):
        pass


def setup(bot):
    bot.add_cog(StyleTransfer(bot))