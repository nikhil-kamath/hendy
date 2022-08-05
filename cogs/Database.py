from random import randint
import discord
from discord.ext import commands, tasks
import mysql.connector
from mysql.connector import Error
from pypika import Query, Column, Table

class Database(commands.Cog):
    """class to handle storing data in databases
    """
    def __init__(self, bot) -> None:
        self.bot = bot
    
    @commands.command()
    async def store(self, ctx, data):
        guild = ctx.guild.id
        connection = None
        cursor = None
        
        try:
            connection_configuration = {
                'user': 'root',
                'password': 'root',
                'host': 'localhost',
                'unix_socket': '/Applications/MAMP/tmp/mysql/mysql.sock',
                'database': 'hendy',
                'raise_on_warnings': True
            }
            connection = mysql.connector.connect(**connection_configuration)

            # sql query to create a table with columns representing message id, user, and message
            create_table_query = f'CREATE TABLE DB_{guild} ( \
                Id int(11) NOT NULL AUTO_INCREMENT, \
                User varchar(250) NOT NULL, \
                Title varchar(5000) NOT NULL, \
                Comment varchar(5000) NOT NULL, \
                Channel varchar(1000) NOT NULL, \
                PRIMARY KEY (Id))'

            cursor = connection.cursor(dictionary=True)
            cursor.execute(create_table_query)
            print(f"Guild ({guild}) has been created")
        
        except mysql.connector.Error as error:
            print(f"failed to create SQL table: {error}")
 
        finally:
            if connection and connection.is_connected():
                test_title = f"hendy video {randint(0, 100)}"
                test_comment = f"i love this video {randint(0, 100)}"
                test_channel = f"hendy channel {randint(0, 100)}"
                
                comment_table = Table(f"DB_{guild}")
                insert_query = Query \
                    .into(comment_table) \
                    .columns("User", "Title", "Comment", "Channel") \
                    .insert(str(ctx.author), test_title, test_comment, test_channel) \
                    .get_sql(quote_char=None)
                
                print("_________________")
                print(insert_query)
                
                cursor.execute(insert_query)
                connection.commit()
                
                await ctx.send("message stored")
                
                cursor.close()
                connection.close()
                print("sql connection has been closed")
                




def setup(bot):
    bot.add_cog(Database(bot))