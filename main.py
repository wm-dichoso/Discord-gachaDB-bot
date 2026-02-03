import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

# import db and services
from database_manager import DatabaseManager
from services import Services

# import commands here
from commands.game_commands import setup_game_commands
from commands.banner_commands import setup_banner_commands

# load all this?
load_dotenv()
db = DatabaseManager()
db.connect_db()
services = Services(db)

# BOT setup
BOT_TOKEN = os.getenv('BOT_TOKEN')
test_CHANNEL_ID = os.getenv('test_CHANNEL_ID')
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not Found.")
        return

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("❌ An internal error occurred.")
        # Optional: log the real error
        raise error.original

    await ctx.send("❌ An unexpected error occurred.")


# Commands here 
setup_game_commands(bot, services)
setup_banner_commands(bot, services)

# just try command XD
@bot.command()
async def h(ctx):
    await ctx.send("hello im alive!!")

# run 
bot.run(BOT_TOKEN)