import discord
from discord.ext import commands, tasks
from PIL import Image
import pathlib
import pytesseract

'''class which allows user to convert images to text files'''
class Passive(commands.Cog):
    def __init__(self, bot = None) -> None:
        self.bot = bot
        self.image_folder = pathlib.Path.cwd() / "resources" / "tesseract" / "images"
        
        print(pytesseract.image_to_pdf_or_hocr(Image.open(self.image_folder / "test1.jpg")))

        