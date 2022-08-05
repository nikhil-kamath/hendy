import json
import discord
from discord.ext import commands, tasks
import os
import random
import utilities.Utilities as Utilities

'''
Class to handle basic statements, insults, and jokes
'''
class Statements(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.statements = set()
        self.statements_channel = 831964747377147934
        self.insult_adjectives = [] # insulting adjectives
        self.insult_adverbs = [] # insulting adverbs
        self.jokes = [] # jokes
        self.all_words = { # used for creating completely random sentences (not only insults)
            "adj": [],
            "adv": [],
            "verb": [],
            "noun": []
        }
        
        self.res_folder = './resources'
        self.word_folder = 'words'
        
        # load all word files
        for key in self.all_words:
            with open(os.path.join(self.res_folder, self.word_folder, f"{key}.json")) as file:
                self.all_words[key] = list(json.load(file))
        
        # load insult adjectives and adverbs
        with open(os.path.join(self.res_folder, self.word_folder, "insult_adj.json")) as file:
            self.insult_adjectives = list(json.load(file))

        with open(os.path.join(self.res_folder, self.word_folder, "insult_adv.json")) as file:
            self.insult_adverbs = list(json.load(file))
            
        # load custom statements
        with open(os.path.join(self.res_folder, 'statements.txt'), 'r') as file:
            for line in file.readlines():
                self.statements.add(line.strip())
                
        # load jokes
        with open(os.path.join(self.res_folder, 'jokes.json')) as file:
            self.jokes = json.load(file)
        
        self.emojis = ["", ":fire:", ":smiling_face_with_3_hearts:", ":heart_eyes:", ":kissing_heart:", ":zany_face:", ":fax:",
                       ":thumbsup:", ":rofl:", ":ok_hand:", ":exclamation:", ":slight_smile:", ":face_vomiting:", ":100:",
                       ":speaking_head:", ":weary:", ":japanese_goblin:", ":skull:", ":joy:", ":grimacing:"]

        
    '''command to see how many statements are saved in the bot'''
    @commands.command()
    async def num(self, ctx):
        await ctx.send(f"Number of things i can say: {len(self.statements)}")
    
    '''main speak command, chooses random thing from saved list'''
    @commands.command(aliases = ["t", "talk"])
    async def speak(self, ctx):
        await ctx.send(random.choice(list(self.statements)))
    
    '''create generic statements. instances of 'adj', 'adv', 'noun', or 'verb' are replaced with 
    a random word from their respective categories'''    
    @commands.command(aliases=['s'])
    async def state(self, ctx, *, statements):
        output = ""
        words = statements.split()
        for word in words:
            if word in self.all_words:  # instances of 'adj', 'adv', 'noun', or 'verb'
                output += f'{random.choice(self.all_words[word])}'
            else:
                output += f'{word} '

        await ctx.send(output)
    
    '''sends a joke. also marks segment of the joke after a question mark as a spoiler'''   
    @commands.command(aliases=['j'])
    async def joke(self, ctx):
        j = random.choice(self.jokes)
        index = -1
        if index := j.find("?") != -1 and index != len(j) -1:
            j = f"{j[:index+1]}||{j[index+1:]}||"
        await(ctx.send(j))

        
    '''insults a given name'''
    @commands.command(aliases=['i'])
    async def insult(self, ctx, *, name):
        adverb = random.choice(self.insult_adverbs)
        adjective = random.choice(self.insult_adjectives)
        await ctx.send(f"{name} is {adverb} {adjective}!! {random.choice(self.emojis)}")
                
    '''change statements modification channel to current one'''
    @commands.command()
    async def setchannel(self, ctx):
        self.statements_channel = ctx.channel.id
    
    '''
    checks messages in the statements_channel for adding and removing custom statements.
    + [message] adds it
    - [message] removes it, if it exists
    '''
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # response cannot trigger on bot messages
            return

        if message.channel.id == self.statements_channel:
            if message.content.startswith('+'):
                to_add = message.content[1:].strip + '\n'
                self.statements.add(to_add)
                with open(os.path.join(self.res_folder, 'statements.txt'), 'a') as writer:
                    writer.write(to_add)
                    
            if message.content.startswith('-'):
                to_remove = message.content[1:].strip()
                if to_remove in self.statements:
                    self.statements.remove(to_remove)
                Utilities.f_remove(os.path.join(self.res_folder, 'statements.txt'), to_remove)
                

def setup(bot):
    bot.add_cog(Statements(bot))
