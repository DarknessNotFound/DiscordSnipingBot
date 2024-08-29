import os
import asyncio
import random
import discord
from DbManagement import CreateSnipesDB, CreateSuperuser
from Logging import CreateLoggingDB
from dotenv import load_dotenv
from discord.ext import commands

print("Sniping Bot application started.")

# Needed for lists of members
intents = discord.Intents.all()
intents.members = True

#Setup the Database (creates tables if they aren't created yet)
CreateLoggingDB()
CreateSnipesDB()

#Load Enviroment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
GUILD = os.getenv('SERVER')
OWNER = os.getenv('OWNER')

#Creates the super user (user of permission level 10)
CreateSuperuser(OWNER)

# Bot and client settings.
client = discord.Client(intents=intents)
bot = commands.Bot(
    command_prefix='>>', 
    intents=intents, 
    case_insensitive=True,
    help_command=commands.MinimalHelpCommand()
    )
# Prints a message to say it connected successfully
# NOTE: Sometimes takes a second to trigger and send msg

@bot.event
async def on_ready():
    print(f"Connected successfully.")
    
@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    
@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
   
@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    
# This searches for all cogs in the cog file and loads the functions for use
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Functions that starts the bot.
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)
        
asyncio.run(main())
